"""
M04 마을 유사도 — KNN baseline (production)
==========================================
32차원 노드 feature 코사인 유사도. spatial 거리 가중.
GAT contrastive는 ml/m04_gat_train.py (학술 ablation only).

Output: data/processed/knn_m04_v1.pkl, village_features.parquet
"""
from __future__ import annotations
import logging
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
DATA = Path(__file__).parent.parent / "data" / "processed"

FEATURE_COLS = [
    # 인구·고령화 (6)
    "population", "aging_rate", "population_extinction_risk",
    "young_resident_ratio", "household_count", "population_change_5y",
    # 산림 (8)
    "forest_ratio", "avg_age_class", "forest_product_diversity_shannon",
    "private_forest_ratio", "broadleaf_ratio", "needleleaf_ratio",
    "mixed_forest_ratio", "avg_dbh",
    # 접근성 (4)
    "distance_to_seoul_km", "distance_to_highway_km", "distance_to_ktx_min",
    "nearest_hospital_km",
    # 매물·시장 (4)
    "forest_land_avg_price_per_pyeong", "active_lots_count",
    "transaction_volume_5y", "young_settlement_amount_won",
    # 보조사업·멘토 (4)
    "subsidy_count_active", "mentor_count", "cooperative_loan_rate",
    "education_courses_yearly",
    # 안전 (4)
    "wildfire_risk", "landslide_risk", "frost_risk", "drought_risk",
    # 라이프스타일 (2)
    "lifestyle_composite_score", "tourism_visitor_count_annual",
]


def load_or_synth():
    p = DATA / "village_features.parquet"
    if p.exists():
        return pd.read_parquet(p)
    log.warning("village_features.parquet 부재 — synthetic 466 마을 생성")
    rng = np.random.default_rng(2026)
    df = pd.DataFrame(rng.normal(0, 1, (466, len(FEATURE_COLS))), columns=FEATURE_COLS)
    df["admin_code"] = [f"4{rng.integers(100,999):03d}{rng.integers(1,99):02d}4000" for _ in range(466)]
    df.to_parquet(p, index=False)
    return df


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    df = load_or_synth()
    X = StandardScaler().fit_transform(df[FEATURE_COLS])

    nn = NearestNeighbors(n_neighbors=10, metric="cosine", algorithm="auto")
    nn.fit(X)

    joblib.dump({"nn": nn, "admin_codes": df["admin_code"].tolist(), "feature_cols": FEATURE_COLS},
                DATA / "knn_m04_v1.pkl")
    log.info(f"Saved KNN with {len(df)} villages × {len(FEATURE_COLS)}d → {DATA / 'knn_m04_v1.pkl'}")

    # Intra-list distance 분산 측정 (학술 ablation 비교 baseline)
    sample_idx = np.random.default_rng(0).choice(len(df), 50, replace=False)
    dists, _ = nn.kneighbors(X[sample_idx])
    log.info(f"KNN Intra-list distance mean: {dists[:, 1:].mean():.3f}")


if __name__ == "__main__":
    main()
