"""
DAG1 — Static SHP 적재 (월 1회)
==============================
FGIS 임상도·산림입지토양도·산지구분도·산림이용기본도 4종 SHP + 466 산촌 boundary
→ PostGIS (SRID 5179, GIST 인덱스) + GeoServer WMS 노출.

W1-T3 산출물.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

DEFAULT_ARGS = {
    "owner": "soop",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
}

DATA_DIR = Path("/opt/airflow/data")
RAW_DIR = DATA_DIR / "raw" / "fgis"
PROCESSED_DIR = DATA_DIR / "processed"

FGIS_DATASETS = [
    # name, FGIS download endpoint hint (실 endpoint는 신청 후 발급, manual fetch 필요)
    {"name": "imsangdo",          "desc": "임상도 1:5,000",       "table": "fgis_imsangdo"},
    {"name": "san_lim_ipji_tojang", "desc": "산림입지 토양도",     "table": "fgis_soil"},
    {"name": "sanji_gubun_do",    "desc": "산지구분도",            "table": "fgis_sanji_gubun"},
    {"name": "sanlim_iyong_gibon", "desc": "산림이용기본도",       "table": "fgis_iyong_gibon"},
]
BOUNDARY_466_URL = "https://www.forest.go.kr/통합자료실/2024_산촌_466_읍면.zip"


def task_check_fgis_files(**ctx):
    """FGIS 무료 신청 SHP 4종이 RAW_DIR에 있는지 확인."""
    missing = []
    for d in FGIS_DATASETS:
        if not (RAW_DIR / f"{d['name']}.shp").exists():
            missing.append(d["name"])
    if missing:
        raise FileNotFoundError(
            f"FGIS SHP 누락: {missing}. map.forest.go.kr에서 무료 신청 후 "
            f"{RAW_DIR}/ 에 압축 해제하세요."
        )
    return [d["name"] for d in FGIS_DATASETS]


def task_load_shp_to_postgis(name: str, table: str, **ctx):
    """ogr2ogr 또는 geopandas로 SHP → PostGIS (SRID 5179)."""
    import geopandas as gpd
    from sqlalchemy import create_engine, text
    import os
    pg_user = os.getenv("POSTGRES_USER", "soop")
    pg_pw   = os.getenv("POSTGRES_PASSWORD", "change_me_in_local")
    pg_host = os.getenv("POSTGRES_HOST", "postgres")
    pg_db   = os.getenv("POSTGRES_DB", "soop")
    engine = create_engine(f"postgresql://{pg_user}:{pg_pw}@{pg_host}:5432/{pg_db}")

    shp_path = RAW_DIR / f"{name}.shp"
    gdf = gpd.read_file(shp_path)
    if gdf.crs is None or gdf.crs.to_epsg() != 5179:
        gdf = gdf.to_crs(epsg=5179)
    gdf.to_postgis(table, engine, if_exists="replace", index=False)

    with engine.begin() as conn:
        conn.execute(text(f"CREATE INDEX IF NOT EXISTS gix_{table} ON {table} USING GIST (geometry)"))
    return f"{table}: {len(gdf):,} features"


def task_load_466_boundary(**ctx):
    """2024 산촌 466 읍면 boundary GeoJSON 적재."""
    import json, geopandas as gpd
    from sqlalchemy import create_engine, text
    import os
    pg_user = os.getenv("POSTGRES_USER", "soop")
    pg_pw   = os.getenv("POSTGRES_PASSWORD", "change_me_in_local")
    engine = create_engine(f"postgresql://{pg_user}:{pg_pw}@{os.getenv('POSTGRES_HOST','postgres')}:5432/{os.getenv('POSTGRES_DB','soop')}")

    geojson_path = RAW_DIR / "sanchon_466.geojson"
    if not geojson_path.exists():
        raise FileNotFoundError(f"{geojson_path} 부재. 산림청 통합자료실 PDF 변환 필요.")

    gdf = gpd.read_file(geojson_path).to_crs(epsg=5179)
    gdf.to_postgis("v_villages", engine, if_exists="replace", index=False)
    with engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS gix_villages ON v_villages USING GIST (geometry)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_villages_admin ON v_villages(admin_code)"))
    return f"v_villages: {len(gdf):,} 산촌"


with DAG(
    dag_id="dag1_static_shp",
    default_args=DEFAULT_ARGS,
    description="FGIS 4종 SHP + 466 산촌 boundary → PostGIS",
    schedule="@monthly",
    start_date=datetime(2026, 5, 12),
    catchup=False,
    tags=["W1-T3", "static", "spatial"],
) as dag:
    check = PythonOperator(task_id="check_fgis_files", python_callable=task_check_fgis_files)

    load_tasks = []
    for d in FGIS_DATASETS:
        t = PythonOperator(
            task_id=f"load_{d['name']}",
            python_callable=task_load_shp_to_postgis,
            op_kwargs={"name": d["name"], "table": d["table"]},
        )
        load_tasks.append(t)

    load_villages = PythonOperator(task_id="load_466_boundary", python_callable=task_load_466_boundary)

    check >> load_tasks >> load_villages
