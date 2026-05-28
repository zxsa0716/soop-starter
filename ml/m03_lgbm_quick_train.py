"""
M03 LightGBM quick train — 합성 features로 학습 파이프라인 검증.
실데이터 도착 시 동일 코드 swap.
"""
from pathlib import Path
import json
import joblib
import lightgbm as lgb
import pandas as pd
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split

DATA = Path(__file__).parent.parent / "data" / "processed"

v = pd.read_parquet(DATA / "village_features_466.parquet")
s = pd.read_parquet(DATA / "suitability_466x52.parquet")

# Join — 마을 feature × 임산물 × 적합도
df = s.merge(v, on="village_code", how="left")

# One-hot product
df = pd.get_dummies(df, columns=["product_code"], prefix="prod")

# Drop string columns
X = df.drop(columns=["suitability_score", "village_code", "sido", "is_dadream_ground_truth"])
y = df["suitability_score"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = lgb.LGBMRegressor(n_estimators=300, learning_rate=0.05, num_leaves=31,
                          random_state=42, verbose=-1)
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], callbacks=[lgb.early_stopping(20)])

y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)

joblib.dump(model, DATA / "lgbm_m03_v3.pkl")
metrics = {
    "synth": True, "r2": float(r2), "mae": float(mae),
    "n_features": X.shape[1], "n_train": len(X_train), "n_test": len(X_test),
    "note": "합성 데이터 학습 — 실데이터(다드림 52품목 + KoMIS + FGIS) 도착 후 swap",
    "ablation_targets": {
        "v0_dadream_baseline": "9 features only (다드림 단독)",
        "v1_komis_30y": "+ 4 KoMIS features → R² target +0.03",
        "v2_nfi_microdata": "+ NFI 임분조사 → R² target +0.05",
        "v3_sentinel_ndvi": "+ Sentinel-2 NDVI seasonality → R² target +0.06"
    }
}
(DATA / "m03_metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False))
print(f'✓ LGBM trained: R²={r2:.3f}, MAE={mae:.3f}')
print(f'✓ model saved: lgbm_m03_v3.pkl ({(DATA / "lgbm_m03_v3.pkl").stat().st_size//1024} KB)')
