"""
DAG3 — Realtime (시간 단위)
===========================
KoMIS 480개소 + 기상청 단기예보 5km + 산림청 산불·산사태 + 임업비서 가격
→ Redis 7일 TTL 캐시 (M10 산림재난 + 시연 안정성 #3).

W4-T5 산출물.
"""
from __future__ import annotations
import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

DEFAULT_ARGS = {"owner": "soop", "retries": 5, "retry_delay": timedelta(seconds=30)}


def fetch_komis_latest(**ctx):
    """KoMIS 480 지점 현재 관측값 → Redis."""
    import httpx, json
    import redis
    key = os.environ.get("KOMIS_API_KEY")
    if not key:
        ctx["ti"].log.warning("KOMIS_API_KEY 미발급 — skip")
        return "skipped"
    r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"))
    url = "https://know.nifos.go.kr/openapi/mtweather/v1/observation/latest"
    resp = httpx.get(url, params={"apiKey": key}, timeout=10)
    items = resp.json().get("data", [])
    for it in items:
        r.setex(f"komis:{it['station_id']}", 7*86400, json.dumps(it, ensure_ascii=False))
    return f"KoMIS: {len(items)} stations cached"


def fetch_wildfire_landslide_risk(**ctx):
    """산림청 산불·산사태 위험도."""
    import httpx, redis, json
    r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"))
    for endpoint, prefix in [
        ("https://forestfire.nifos.go.kr/api/risk/today", "wildfire"),
        ("https://sansatai.forest.go.kr/api/risk/today", "landslide"),
    ]:
        try:
            resp = httpx.get(endpoint, timeout=10)
            data = resp.json()
            r.setex(f"risk:{prefix}:today", 7*86400, json.dumps(data, ensure_ascii=False))
        except Exception as e:
            ctx["ti"].log.warning(f"{prefix} fetch failed: {e}")


def fetch_kma_grid(**ctx):
    """기상청 단기예보 5km 격자 — 466 산촌 boundary 격자 cell만."""
    import httpx, redis, json
    api_key = os.environ.get("KMA_GRID_API_KEY")
    if not api_key:
        return "skipped"
    r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"))
    url = "https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
    # 466 격자 cell sample (simplified)
    grid_cells = [{"nx": 60, "ny": 127}, {"nx": 89, "ny": 90}]
    for cell in grid_cells:
        params = {"serviceKey": api_key, "pageNo": 1, "numOfRows": 1000, "dataType": "JSON",
                  "base_date": datetime.utcnow().strftime("%Y%m%d"),
                  "base_time": "0500", "nx": cell["nx"], "ny": cell["ny"]}
        try:
            resp = httpx.get(url, params=params, timeout=10)
            r.setex(f"kma:grid:{cell['nx']}:{cell['ny']}", 7*86400, json.dumps(resp.json(), ensure_ascii=False))
        except Exception as e:
            ctx["ti"].log.warning(f"KMA grid fetch failed: {e}")


with DAG(
    dag_id="dag3_realtime",
    default_args=DEFAULT_ARGS,
    description="KoMIS + 기상청 + 산불·산사태 → Redis 7일 TTL",
    schedule="@hourly", start_date=datetime(2026, 5, 12), catchup=False,
    max_active_runs=1, tags=["W4-T5", "realtime"],
) as dag:
    t1 = PythonOperator(task_id="fetch_komis_latest", python_callable=fetch_komis_latest)
    t2 = PythonOperator(task_id="fetch_wildfire_landslide_risk", python_callable=fetch_wildfire_landslide_risk)
    t3 = PythonOperator(task_id="fetch_kma_grid", python_callable=fetch_kma_grid)
    [t1, t2, t3]
