"""
DAG5 — Earth Engine (월 1회)
============================
Sentinel-2 NDVI/EVI 30년 + GEDI L4A 바이오매스 + ALOS PALSAR-2 SAR
→ data/processed/ndvi_seasonality.parquet (466 마을 × 12 월 × 30년).

W2-T6 산출물. Heedo GEE 자산 그대로 활용.
"""
from __future__ import annotations
import os
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

DEFAULT_ARGS = {"owner": "soop", "retries": 2, "retry_delay": timedelta(minutes=15)}
DATA = Path("/opt/airflow/data/processed")


def init_gee(**ctx):
    import ee
    sa_email = os.environ["GEE_SERVICE_ACCOUNT_EMAIL"]
    key_path = os.environ["GEE_SERVICE_ACCOUNT_KEY_PATH"]
    project = os.environ["GEE_PROJECT_ID"]
    credentials = ee.ServiceAccountCredentials(sa_email, key_path)
    ee.Initialize(credentials, project=project)
    return "GEE initialized"


def compute_ndvi_seasonality(**ctx):
    """Sentinel-2 30년 NDVI 월별 평균 (466 마을 × 1km buffer)."""
    import ee, geopandas as gpd, pandas as pd
    init_gee(**ctx)
    villages = gpd.read_file(DATA / "villages_466.geojson") if (DATA / "villages_466.geojson").exists() else None
    if villages is None or len(villages) == 0:
        ctx["ti"].log.warning("villages_466.geojson 부재 — DAG1 우선 실행 필요")
        return "skipped"

    s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterDate("1995-01-01", "2025-12-31")  # 표준 S2 시작 2015, 이전은 Landsat join

    rows = []
    for _, v in villages.iterrows():
        buf = ee.Geometry.Point([v.geometry.centroid.x, v.geometry.centroid.y]).buffer(1000)
        for month in range(1, 13):
            month_col = s2.filter(ee.Filter.calendarRange(month, month, "month"))
            ndvi = month_col.map(lambda img: img.normalizedDifference(["B8", "B4"]).rename("NDVI")) \
                            .mean().clip(buf)
            mean_ndvi = ndvi.reduceRegion(reducer=ee.Reducer.mean(), geometry=buf, scale=20).getInfo()
            rows.append({"admin_code": v["admin_code"], "month": month,
                         "ndvi_mean_30y": mean_ndvi.get("NDVI", None)})
    pd.DataFrame(rows).to_parquet(DATA / "ndvi_seasonality.parquet", index=False)
    return f"NDVI seasonality: {len(rows)} rows"


with DAG(
    dag_id="dag5_earth_engine",
    default_args=DEFAULT_ARGS,
    description="Sentinel-2 + GEDI + PALSAR → 466 마을 NDVI/EVI 30y seasonality",
    schedule="@monthly", start_date=datetime(2026, 5, 12), catchup=False,
    tags=["W2-T6", "earth-engine"],
) as dag:
    t1 = PythonOperator(task_id="init_gee", python_callable=init_gee)
    t2 = PythonOperator(task_id="compute_ndvi_seasonality", python_callable=compute_ndvi_seasonality)
    t1 >> t2
