"""
M02 + M11 — 466 산촌 읍면 후보 및 4축 score.
"""
from typing import Optional
from pydantic import BaseModel, Field, confloat, conint


class RadarAxes(BaseModel):
    """
    마을 카드 4축 레이더 — 박지영 위원 사용자 체감 + 이상호 위원 정책 fit 동시 충족.
    """
    forestry_fit: confloat(ge=0, le=1) = Field(..., description="임업 적합도 (M3 LGBM aggregate)")
    lifestyle: confloat(ge=0, le=1) = Field(..., description="M11 라이프스타일 4축 평균")
    policy_match: confloat(ge=0, le=1) = Field(..., description="정착지원금·후계자 매칭 비율")
    safety: confloat(ge=0, le=1) = Field(..., description="1 - 산불·산사태 위험도")


class VillageScore(BaseModel):
    """M02 multi-axis filter 산출 점수."""
    spatial: confloat(ge=0, le=1)
    lifestyle: confloat(ge=0, le=1)
    safety: confloat(ge=0, le=1)
    composite: confloat(ge=0, le=1) = Field(
        ..., description="가중 합산 (사용자 라이프스타일 가중치 적용)"
    )


class Village(BaseModel):
    """
    466 산촌 읍면 중 하나 (산림기본법 §3 분류 + 2024 산촌기초조사).
    """
    admin_code: str = Field(..., description="법정동 코드 10자리")
    name: str = Field(..., description="예: '강원특별자치도 평창군 진부면'")
    sido: str
    sigungu: str
    eupmyeondong: str

    # 인구·고령화
    population: conint(ge=0)
    aging_rate: confloat(ge=0, le=1) = Field(..., description="65세 이상 비율")
    population_extinction_risk: confloat(ge=0, le=1) = Field(
        ..., description="소멸위험지수 1.0 = 임계점"
    )

    # 산림 지표
    forest_ratio: confloat(ge=0, le=1)
    avg_age_class: confloat(ge=1, le=10) = Field(..., description="임령 영급 1~10")
    forest_product_diversity_shannon: confloat(ge=0)

    # 접근성
    distance_to_seoul_km: confloat(ge=0)
    distance_to_ktx_min: Optional[confloat(ge=0)] = None
    distance_to_highway_km: confloat(ge=0)
    nearest_hospital_km: confloat(ge=0)

    # 매물 지표
    forest_land_avg_price_per_pyeong: Optional[int] = None
    active_lots_count: conint(ge=0) = 0

    # 정책
    has_young_settlement_subsidy: bool = False
    young_settlement_amount_won: Optional[int] = None
    has_2026_new_policy_hit: list[str] = Field(
        default_factory=list,
        description="예: ['산촌체류형 쉼터', '영양 스마트팜 105억']",
    )

    # 라이프스타일 5km POI 카운트 (M11)
    nearby_chiyu_forests: conint(ge=0) = 0
    nearby_recreation_forests: conint(ge=0) = 0
    nearby_peaks: conint(ge=0) = 0
    nearby_trails_km: confloat(ge=0) = 0.0

    # 안전
    wildfire_risk: confloat(ge=0, le=1)
    landslide_risk: confloat(ge=0, le=1)

    # 4축 레이더 (M02 + M11 합산)
    radar: Optional[RadarAxes] = None
    score: Optional[VillageScore] = None

    # 멘토·조합 (M09 직결)
    cooperative_id: Optional[str] = Field(None, description="142 산림조합 ID")
    mentor_count: conint(ge=0) = 0
