#!/bin/bash
# =============================================================================
# PostgreSQL + PostGIS 초기화
# - Airflow 메타 DB 생성
# - PostGIS 확장 활성화
# - 기본 schema 생성
# =============================================================================
set -e

POSTGRES_DB="${POSTGRES_DB:-soop}"
POSTGRES_USER="${POSTGRES_USER:-soop}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
  -- Airflow 메타 DB
  CREATE DATABASE airflow OWNER ${POSTGRES_USER};

  -- soop DB에 PostGIS 활성화
  \c ${POSTGRES_DB}
  CREATE EXTENSION IF NOT EXISTS postgis;
  CREATE EXTENSION IF NOT EXISTS postgis_topology;
  CREATE EXTENSION IF NOT EXISTS pg_trgm;

  -- 466 산촌 boundary 테이블 (DAG1이 실제 채움)
  CREATE TABLE IF NOT EXISTS v_villages (
    admin_code           VARCHAR(10) PRIMARY KEY,
    name                 TEXT,
    sido                 TEXT,
    sigungu              TEXT,
    eupmyeondong         TEXT,
    population           INT,
    aging_rate           FLOAT,
    forest_ratio         FLOAT,
    distance_to_seoul_km FLOAT,
    is_sanchon           BOOLEAN DEFAULT TRUE,
    spatial_score        FLOAT,
    lifestyle_score      FLOAT,
    safety_score         FLOAT,
    geometry             geometry(MultiPolygon, 5179)
  );
  CREATE INDEX IF NOT EXISTS gix_v_villages ON v_villages USING GIST(geometry);

  -- 라이프스타일 POI 통합 테이블 (W1-T7이 채움)
  CREATE TABLE IF NOT EXISTS lifestyle_poi (
    id           SERIAL PRIMARY KEY,
    category     VARCHAR(50),
    name         TEXT,
    geometry     geometry(Point, 5179)
  );
  CREATE INDEX IF NOT EXISTS gix_lifestyle_poi ON lifestyle_poi USING GIST(geometry);
EOSQL

echo "PostgreSQL + PostGIS init 완료"
