#!/bin/bash
# 4 페르소나 시연용 최소 데이터 시드 + 캐시 grid 생성
set -e

echo "▶ Seed demo: 4 페르소나 fixture + 93k grid (synthetic prior 사용)"

docker compose exec backend python -m ml.m05_mc_calibration
docker compose exec backend python -m ml.m05_grid_precompute --trajectories 5000 --products 5
docker compose exec backend python -m ml.m03_lgbm_train --stage all --save
docker compose exec backend python -m ml.m04_knn_train

echo ""
echo "✅ Demo seed 완료. 다음으로:"
echo "    curl http://localhost:8000/persona/p01 | jq ."
echo "    open http://localhost:3000/demo"
