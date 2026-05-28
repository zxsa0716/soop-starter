"""
DAG2 — Statistics 통계 수집 (월 1회)
====================================
산림자원통계 OpenAPI + KOSIS API. 임가경제 1,500가구 8업종 분포 →
M5 calibration prior로 직결.

W1-T4 산출물.
"""
from __future__ import annotations
import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

DEFAULT_ARGS = {"owner": "soop", "retries": 3, "retry_delay": timedelta(minutes=5)}
DATA = Path("/opt/airflow/data/processed")


def fetch_forest_family_economy(**ctx):
    """산림자원통계 OpenAPI — 임가경제조사 1,500가구."""
    import httpx, pandas as pd, duckdb
    key = os.environ["KFS_FRSAS1_KEY"]
    url = "https://apis.data.go.kr/1400000/frsas1/getForestFamilyEconomyList"
    rows = []
    for page in range(1, 20):
        r = httpx.get(url, params={"serviceKey": key, "numOfRows": 100, "pageNo": page,
                                   "type": "json"}, timeout=15)
        r.raise_for_status()
        items = r.json().get("response", {}).get("body", {}).get("items", {}).get("item", [])
        if not items:
            break
        rows.extend(items if isinstance(items, list) else [items])

    df = pd.DataFrame(rows)
    DATA.mkdir(parents=True, exist_ok=True)
    df.to_parquet(DATA / "forest_family_economy_raw.parquet", index=False)

    con = duckdb.connect(str(DATA / "stats.duckdb"))
    con.execute("DROP TABLE IF EXISTS forest_family_economy")
    con.register("df_v", df)
    con.execute("CREATE TABLE forest_family_economy AS SELECT * FROM df_v")
    con.close()
    return f"forest_family_economy: {len(df):,} rows"


def fetch_forest_product_production(**ctx):
    """임산물생산조사 14종 145품목."""
    import httpx, pandas as pd, duckdb
    key = os.environ["KFS_FRSAS1_KEY"]
    url = "https://apis.data.go.kr/1400000/frsas1/getForestProductProductionList"
    rows = []
    for page in range(1, 50):
        r = httpx.get(url, params={"serviceKey": key, "numOfRows": 100, "pageNo": page, "type": "json"}, timeout=15)
        r.raise_for_status()
        items = r.json().get("response", {}).get("body", {}).get("items", {}).get("item", [])
        if not items: break
        rows.extend(items if isinstance(items, list) else [items])

    df = pd.DataFrame(rows)
    df.to_parquet(DATA / "forest_product_production_raw.parquet", index=False)
    return f"forest_product_production: {len(df):,} rows"


def fetch_kosis_population(**ctx):
    """KOSIS — 임가소득·고령화·소멸지수."""
    import httpx, pandas as pd
    key = os.environ.get("KOSIS_API_KEY", "")
    if not key:
        ctx["ti"].log.warning("KOSIS_API_KEY 미발급 — skip")
        return "skipped"
    url = "https://kosis.kr/openapi/Param/statisticsParameterData.do"
    # 표 ID는 마이페이지에서 확인
    params = {"method": "getList", "apiKey": key, "format": "json", "jsonVD": "Y",
              "orgId": "101", "tblId": "DT_1IN1502", "itmId": "T20", "objL1": "ALL", "prdSe": "Y", "newEstPrdCnt": 5}
    r = httpx.get(url, params=params, timeout=15)
    df = pd.DataFrame(r.json() if r.status_code == 200 else [])
    df.to_parquet(DATA / "kosis_aging.parquet", index=False)
    return f"kosis_aging: {len(df):,} rows"


def build_calibration_prior(**ctx):
    """M05 calibration prior — 임가경제 8업종 분포 → parquet (m05_grid_precompute.py 입력)."""
    import duckdb
    con = duckdb.connect(str(DATA / "stats.duckdb"), read_only=True)
    df = con.execute(
        "SELECT category, annual_income_won FROM forest_family_economy"
    ).fetchdf()
    con.close()
    df = df.rename(columns={"annual_income_won": "observed"}) if "annual_income_won" in df.columns else df
    df.to_parquet(DATA / "nong_eo_chon_8eopjong.parquet", index=False)
    return f"calibration prior: {len(df):,} 가구"


with DAG(
    dag_id="dag2_statistics",
    default_args=DEFAULT_ARGS,
    description="산림자원통계 + KOSIS → DuckDB stats.db + M05 calibration prior",
    schedule="@monthly", start_date=datetime(2026, 5, 12), catchup=False,
    tags=["W1-T4", "statistics"],
) as dag:
    t1 = PythonOperator(task_id="fetch_forest_family_economy", python_callable=fetch_forest_family_economy)
    t2 = PythonOperator(task_id="fetch_forest_product_production", python_callable=fetch_forest_product_production)
    t3 = PythonOperator(task_id="fetch_kosis_population", python_callable=fetch_kosis_population)
    t4 = PythonOperator(task_id="build_calibration_prior", python_callable=build_calibration_prior)

    [t1, t2, t3] >> t4
