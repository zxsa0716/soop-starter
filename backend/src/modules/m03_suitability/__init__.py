"""
M03 임산물 적합도 매칭
======================
LightGBM 다중 출력 분류. 28차원 feature × 52 단기임산물.

학술 정직성 (김재현 위원 강제):
  - 다드림 baseline (9d) vs 우리 enriched (28d) ablation R² 비교
  - SHAP TreeExplainer로 자동 해설 ("왜 평창에 표고가 적합한가")
"""
from .recommender import recommend_forest_products

__all__ = ["recommend_forest_products"]
