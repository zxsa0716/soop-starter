"""
W1-T8 — KoMIS 산악기상 480개소 30년 일괄 다운로드
================================================
mtweather.nifos.go.kr OpenAPI / 일괄 다운로드.
raw ~200GB → MinIO. 일별 평균은 DuckDB로 down-sample.

Usage:
  python scripts/download_komis_30y.py --stations all --years 1995-2025
"""
from __future__ import annotations
import argparse
import logging
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import duckdb
import httpx

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

DATA = Path(__file__).parent.parent / "data"
RAW = DATA / "raw" / "komis"
PROCESSED = DATA / "processed"

API_BASE = "https://know.nifos.go.kr/openapi/mtweather/v1"
DEFAULT_STATIONS = list(range(1, 481))  # KoMIS 480 지점


def fetch_station_list(**kwargs) -> list[int]:
    """station_id list. API 부재 시 1~480."""
    key = os.environ.get("KOMIS_API_KEY")
    if not key:
        return DEFAULT_STATIONS
    r = httpx.get(f"{API_BASE}/stations", params={"apiKey": key}, timeout=15)
    if r.status_code != 200:
        return DEFAULT_STATIONS
    return [s["id"] for s in r.json().get("data", [])]


def download_year(station_id: int, year: int, key: str):
    """단일 지점 단일 연도 1분 단위 raw CSV → MinIO upload + 일별 평균 DuckDB."""
    RAW.mkdir(parents=True, exist_ok=True)
    out_csv = RAW / f"komis_{station_id:03d}_{year}.csv"
    if out_csv.exists():
        return out_csv

    url = f"{API_BASE}/observation/yearly"
    params = {"apiKey": key, "stationId": station_id, "year": year, "format": "csv"}
    with httpx.stream("GET", url, params=params, timeout=60) as r:
        r.raise_for_status()
        with out_csv.open("wb") as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
    return out_csv


def down_sample_to_daily():
    """raw 1분 → DuckDB 일별 평균 + QC."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(PROCESSED / "komis_daily.duckdb"))
    con.execute("DROP TABLE IF EXISTS komis_daily")
    con.execute(f"""
      CREATE TABLE komis_daily AS
      SELECT
        station_id,
        CAST(strftime('%Y-%m-%d', observation_time) AS DATE) AS day,
        AVG(temp_c) AS temp_avg_c,
        MIN(temp_c) AS temp_min_c,
        MAX(temp_c) AS temp_max_c,
        SUM(precip_mm) AS precip_sum_mm,
        AVG(wind_ms) AS wind_avg_ms,
        AVG(humidity_pct) AS humidity_avg_pct
      FROM read_csv_auto('{RAW}/komis_*.csv', union_by_name=True)
      WHERE qc_flag = 'OK'
      GROUP BY station_id, day
    """)
    n = con.execute("SELECT COUNT(*) FROM komis_daily").fetchone()[0]
    con.close()
    log.info(f"komis_daily: {n:,} rows")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", default="1995-2025")
    parser.add_argument("--stations", default="all")
    args = parser.parse_args()

    key = os.environ.get("KOMIS_API_KEY")
    if not key:
        log.error("KOMIS_API_KEY 미발급. docs/01-api-application-guide.md 참고.")
        return

    start_y, end_y = map(int, args.years.split("-"))
    stations = fetch_station_list() if args.stations == "all" else [int(s) for s in args.stations.split(",")]

    for st in stations:
        for y in range(start_y, end_y + 1):
            try:
                download_year(st, y, key)
                time.sleep(0.5)  # rate limit
            except Exception as e:
                log.warning(f"st={st} y={y} failed: {e}")
    down_sample_to_daily()


if __name__ == "__main__":
    main()
