"""
M03 — 임산물 적합도 매칭 (LightGBM + 다드림 baseline ablation).
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, confloat, conint


class ProductCategory(str, Enum):
    mushroom = "버섯"       # 표고·느타리·목이
    herb = "약초"           # 산양삼·도라지·약초
    nut = "견과"            # 밤·잣·호두
    fruit = "과실"          # 대추·복분자·산딸기
    sap = "수액"            # 고로쇠·자작나무 수액
    bark = "수피·약재"      # 황칠·헛개
    leaf = "잎"             # 곰취·어수리·산나물
    root = "뿌리"           # 작약·산수유


class ShapValue(BaseModel):
    """모델 추천 이유 자동 생성용 (M3 SHAP TreeExplainer)."""
    feature: str = Field(..., description="예: '연평균 기온'")
    value: float = Field(..., description="해당 마을의 raw feature 값")
    shap: float = Field(..., description="이 추천에 기여한 부호·크기 (-1~+1 정규화)")
    direction: str = Field(..., description="'positive' or 'negative'")
    plain_text: str = Field(..., description="자연어 설명, 예: '연평균 8.2℃가 표고 균사 활성에 적합'")


class ForestProduct(BaseModel):
    """52 단기임산물 카탈로그 (다드림 ground truth)."""
    code: str = Field(..., description="다드림 품목 코드")
    name_ko: str
    name_sci: Optional[str] = None
    category: ProductCategory
    cycle_years: conint(ge=1, le=10) = Field(..., description="첫 수확까지 연수")
    typical_initial_cost_per_ha_won: int
    typical_annual_yield_kg_per_ha: float
    typical_price_per_kg_won_p50: int
    smart_farm_eligible: bool = False
    koc_eligible: bool = False
    description: str = ""


class ForestProductRecommendation(BaseModel):
    """M03 출력 카드 한 장."""
    product: ForestProduct
    score: confloat(ge=0, le=1) = Field(..., description="LGBM 적합도 (다드림 baseline + enriched feature)")
    confidence_interval: tuple[float, float]
    expected_yield_kg_per_ha: float
    standard_initial_cost_won: int
    typical_5yr_revenue: dict[str, int] = Field(
        ..., description="{'p10': ..., 'p50': ..., 'p90': ...} 단위: 원"
    )
    shap_values: list[ShapValue] = Field(default_factory=list, max_length=5)
    citation_dadream_url: Optional[str] = Field(
        None, description="다드림 재배적지도 해당 품목 link (baseline 출처)"
    )
