#!/bin/bash
# =============================================================================
# Soop Starter — 로컬 개발 셋업
# =============================================================================
set -e

echo ""
echo "▶ Soop Starter 셋업"
echo "─────────────────────────"

# .env
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✅ .env 생성됨. docs/01-api-application-guide.md 참고하여 API 키 8종 입력 후 재실행."
  exit 1
fi

# Docker
if ! command -v docker &> /dev/null; then
  echo "❌ Docker 미설치. https://docs.docker.com/get-docker/ 설치 후 재실행."
  exit 1
fi

# MinIO 버킷 사전 생성
docker compose up -d minio
sleep 5
docker compose exec -T minio mc alias set local http://localhost:9000 "$MINIO_ACCESS_KEY" "$MINIO_SECRET_KEY" || true
docker compose exec -T minio mc mb -p local/soop-raw     || true
docker compose exec -T minio mc mb -p local/soop-models  || true

# 전체 기동
docker compose up -d

echo ""
echo "✅ 전체 7 컨테이너 기동"
echo "    Frontend : http://localhost:3000"
echo "    Backend  : http://localhost:8000/docs"
echo "    Airflow  : http://localhost:8080  (admin/admin)"
echo "    MinIO    : http://localhost:9001"
echo ""
echo "다음:"
echo "  1) docker compose exec airflow airflow dags trigger dag1_static_shp"
echo "  2) ml/m05_grid_precompute.py 실행 (93,000 시나리오)"
echo "  3) 4 페르소나 시연: curl http://localhost:8000/persona/p01"
