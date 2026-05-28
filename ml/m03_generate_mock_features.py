"""
M03 학습 데이터 generator — 466 마을 × 52 임산물 × 28 features 합성.

용도:
  - 실제 다드림 + KoMIS + FGIS 데이터 적재 전에도 학습 파이프라인 검증.
  - W2-T1 (features.parquet) → W2-T2 (LGBM 학습) 단축.
  - 실데이터 도착 시 동일 schema로 swap.

학술 정직성:
  - 합성 데이터임을 명시 (synth=True flag in metadata).
  - 임가경제조사 8업종 분포 prior와 호환되는 noise.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path(__file__).parent.parent / "data" / "processed"
DATA.mkdir(parents=True, exist_ok=True)


def generate_mock_features(n_villages: int = 466, n_products: int = 52, seed: int = 42):
    rng = np.random.default_rng(seed)

    # 466 마을 base features
    villages = []
    for i in range(n_villages):
        sido = rng.choice(["강원특별자치도", "충청북도", "충청남도", "전북특별자치도",
                           "전라남도", "경상북도", "경상남도", "강원특별자치도"])
        villages.append({
            "village_code": f"V_{i:04d}",
            "sido": sido,
            # 토양 (4d)
            "soil_ph": float(np.clip(rng.normal(5.8, 0.4), 4.5, 7.5)),
            "soil_organic_pct": float(np.clip(rng.normal(3.0, 0.8), 0.5, 8)),
            "soil_depth_cm": int(float(np.clip(rng.normal(80, 25), 30, 200))),
            "soil_type_loam": float(rng.random() < 0.6),
            # 산악기상 30y mean (4d)
            "temp_30y_mean_c": float(np.clip(rng.normal(10.5, 2.5), 3, 16)),
            "precip_30y_mean_mm": float(np.clip(rng.normal(1300, 250), 800, 2000)),
            "sunshine_30y_mean_h": float(np.clip(rng.normal(2200, 200), 1700, 2700)),
            "frost_days_30y_mean": int(float(np.clip(rng.normal(60, 18), 20, 130))),
            # DEM (3d)
            "elevation_m": rng.uniform(150, 1200),
            "slope_deg": rng.uniform(5, 35),
            "aspect_north_pct": rng.uniform(0, 1),
            # 임상 (3d)
            "forest_cover_pct": rng.uniform(0.55, 0.95),
            "avg_age_class": rng.uniform(2, 7),
            "dominant_species_pinus": float(rng.random() < 0.55),
            # NDVI seasonality (6d, 12 months → quarterly + amplitude)
            "ndvi_q1": rng.uniform(0.2, 0.4),
            "ndvi_q2": rng.uniform(0.5, 0.85),
            "ndvi_q3": rng.uniform(0.6, 0.9),
            "ndvi_q4": rng.uniform(0.3, 0.5),
            "ndvi_annual_amplitude": rng.uniform(0.3, 0.6),
            "evi_annual_amplitude": rng.uniform(0.25, 0.55),
            # 정책·접근성 (5d)
            "distance_to_seoul_km": rng.uniform(70, 380),
            "ktx_min": rng.uniform(12, 180),
            "young_subsidy_amount_won": rng.choice([0, 5_000_000, 8_000_000, 10_000_000, 15_000_000]),
            "wildfire_risk": rng.uniform(0.08, 0.32),
            "landslide_risk": rng.uniform(0.10, 0.30),
            # 인구
            "population": int(np.clip(rng.lognormal(7.5, 0.9), 300, 12000)),
            "aging_rate": rng.uniform(0.30, 0.62),
        })

    villages_df = pd.DataFrame(villages)
    villages_df.to_parquet(DATA / "village_features_466.parquet")

    # 52 임산물 × 466 마을 적합도 score (다드림 baseline)
    products = [{"product_code": f"P_{j:03d}", "product_name": f"임산물_{j:02d}",
                 "category": rng.choice(["mushroom", "herb", "nut", "fruit", "sap", "bark", "leaf", "root"])}
                for j in range(n_products)]
    products_df = pd.DataFrame(products)
    products_df.to_parquet(DATA / "products_52.parquet")

    # 466×52 적합도 매트릭스 (LGBM 학습 target)
    rows = []
    for i, v in enumerate(villages):
        for j, p in enumerate(products):
            # 합성 적합도 = 비선형 함수 of 일부 feature
            base = 0.5
            base += 0.15 * (v["temp_30y_mean_c"] - 6) / 10  # 온도
            base += 0.20 * v["forest_cover_pct"]            # 산림 피복
            base += 0.10 * (v["soil_organic_pct"] / 5)
            base += rng.normal(0, 0.08)                       # noise
            # 품목별 편향
            if p["category"] == "mushroom" and v["forest_cover_pct"] > 0.75:
                base += 0.12
            if p["category"] == "herb" and 0.30 < v["aging_rate"] < 0.50:
                base += 0.05
            rows.append({
                "village_code": v["village_code"],
                "product_code": p["product_code"],
                "suitability_score": float(np.clip(base, 0, 1)),
                "is_dadream_ground_truth": float(rng.random() < 0.85),
            })
    suit_df = pd.DataFrame(rows)
    suit_df.to_parquet(DATA / "suitability_466x52.parquet")

    # Metadata + schema
    meta = {
        "synth": True,
        "generated_by": "ml/m03_generate_mock_features.py",
        "seed": seed,
        "n_villages": n_villages,
        "n_products": n_products,
        "n_features": 28,
        "note": "Replace with real data: FGIS 임상도·토양도 + KoMIS 30y + Sentinel-2 NDVI + 다드림 52품목.",
        "swap_targets": [
            "village_features_466.parquet → DAG1 + DAG2 + DAG5 outputs",
            "products_52.parquet → 다드림 52품목 catalog (gis.kofpi.or.kr)",
            "suitability_466x52.parquet → 다드림 재배적지 supervised label",
        ],
    }
    (DATA / "m03_synth_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return villages_df, products_df, suit_df, meta


if __name__ == "__main__":
    v, p, s, meta = generate_mock_features()
    print(f"✓ village_features_466.parquet: {len(v)} rows × {len(v.columns)} cols")
    print(f"✓ products_52.parquet: {len(p)} products")
    print(f"✓ suitability_466x52.parquet: {len(s)} rows (target = suitability_score)")
    print(f"✓ m03_synth_meta.json: synth={meta['synth']}, seed={meta['seed']}")
