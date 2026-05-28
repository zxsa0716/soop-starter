"""
W1-T7 — 산림복지·등산트레킹센터 5개 데이터셋 통합 (M11 라이프스타일 score backbone)
==================================================================================
- 15110279 치유의숲 좌표
- 15013111 자연휴양림 표준데이터
- 15108062 봉우리 POI
- 15125108 숲길 편의시설 POI
- 15002725 둘레길 SHP

→ PostGIS lifestyle_poi 테이블 + 466 마을 5km 반경 사전 indexing.
"""
from __future__ import annotations
import logging
import os
from pathlib import Path

import geopandas as gpd
import pandas as pd
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

DATA = Path(__file__).parent.parent / "data"
RAW = DATA / "raw" / "lifestyle"

DATASETS = [
    {"id": "15110279", "category": "chiyu_forest", "format": "csv",
     "download_url": "https://www.data.go.kr/data/15110279/fileData.do",
     "lat_col": "위도", "lon_col": "경도", "name_col": "치유의숲명"},
    {"id": "15013111", "category": "recreation",   "format": "csv",
     "download_url": "https://www.data.go.kr/data/15013111/fileData.do",
     "lat_col": "위도", "lon_col": "경도", "name_col": "휴양림명"},
    {"id": "15108062", "category": "peak",         "format": "csv",
     "download_url": "https://www.data.go.kr/data/15108062/fileData.do",
     "lat_col": "위도", "lon_col": "경도", "name_col": "봉우리명"},
    {"id": "15125108", "category": "trail_facility", "format": "csv",
     "download_url": "https://www.data.go.kr/data/15125108/fileData.do"},
    {"id": "15002725", "category": "trail",        "format": "shp",
     "download_url": "https://www.data.go.kr/data/15002725/fileData.do"},
]


def load_one(ds: dict) -> gpd.GeoDataFrame:
    """단일 데이터셋 로드 → 표준 columns: category, name, geometry."""
    candidates = list(RAW.glob(f"{ds['id']}*")) + list(RAW.glob(f"*{ds['category']}*"))
    if not candidates:
        log.warning(f"{ds['id']} ({ds['category']}) 파일 부재 → skip. 다운로드: {ds['download_url']}")
        return gpd.GeoDataFrame(columns=["category", "name", "geometry"], crs="EPSG:5179")

    f = candidates[0]
    if ds["format"] == "csv":
        df = pd.read_csv(f, encoding="cp949")
        if "lat_col" in ds and ds["lat_col"] in df.columns:
            geom = gpd.points_from_xy(df[ds["lon_col"]], df[ds["lat_col"]])
            gdf = gpd.GeoDataFrame(df, geometry=geom, crs="EPSG:4326").to_crs(5179)
            gdf = gdf.rename(columns={ds["name_col"]: "name"})
        else:
            return gpd.GeoDataFrame(columns=["category", "name", "geometry"], crs="EPSG:5179")
    else:  # shp
        gdf = gpd.read_file(f).to_crs(5179)
        if "name" not in gdf.columns and "NAME" in gdf.columns:
            gdf = gdf.rename(columns={"NAME": "name"})

    gdf["category"] = ds["category"]
    keep_cols = [c for c in ["category", "name", "geometry"] if c in gdf.columns]
    return gdf[keep_cols]


def main():
    engine = create_engine(
        f"postgresql://{os.getenv('POSTGRES_USER', 'soop')}:"
        f"{os.getenv('POSTGRES_PASSWORD', 'change_me_in_local')}@"
        f"{os.getenv('POSTGRES_HOST', 'localhost')}:5432/{os.getenv('POSTGRES_DB', 'soop')}"
    )

    frames = [load_one(ds) for ds in DATASETS]
    combined = pd.concat([g for g in frames if not g.empty], ignore_index=True)
    if combined.empty:
        log.warning("모든 데이터셋 부재 — RAW_DIR에 5종 다운로드 후 재실행")
        return

    log.info(f"통합 POI: {len(combined):,} 개")
    combined.to_postgis("lifestyle_poi", engine, if_exists="replace", index=False)
    with engine.begin() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS gix_lifestyle_poi ON lifestyle_poi USING GIST(geometry)"))
        # 466 마을 5km 반경 materialized view 사전 계산
        conn.execute(text("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS v_lifestyle_poi_buffered AS
            SELECT v.admin_code AS village_admin_code,
                   p.category,
                   p.name,
                   ST_Distance(v.geometry, p.geometry) / 1000.0 AS distance_km
            FROM v_villages v
            JOIN lifestyle_poi p
              ON ST_DWithin(v.geometry, p.geometry, 5000)
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_buf_village ON v_lifestyle_poi_buffered(village_admin_code)"))
    log.info("v_lifestyle_poi_buffered (5km radius materialized) 생성 완료")


if __name__ == "__main__":
    main()
