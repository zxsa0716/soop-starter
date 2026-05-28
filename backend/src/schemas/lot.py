"""
M07 — 임야 매물 · 산촌체류형 쉼터 입지 평가.
"""
from typing import Optional
from pydantic import BaseModel, Field, confloat, conint


class Lot(BaseModel):
    """임야 매물 한 건 (산림조합 임야거래장터 + 일별토지임야 + BYOA 다드림 결합)."""
    pnu: str = Field(..., min_length=19, max_length=19, description="필지 고유번호 19자리")
    admin_code: str
    area_ha: confloat(ge=0)
    price_won: Optional[int] = None
    price_per_pyeong_won: Optional[int] = None

    # 산지구분도 (FGIS)
    is_im_eob_yong_sanji: bool = Field(..., description="임업용 산지 ✅ 여부 (쉼터 prereq)")
    is_bo_jeon_sanji: bool = False
    is_jun_bo_jeon_sanji: bool = False

    # 산림 지표
    forest_type: Optional[str] = None
    avg_age_class: Optional[confloat(ge=1, le=10)] = None
    slope_deg: Optional[confloat(ge=0, le=90)] = None
    aspect: Optional[str] = None
    elevation_m: Optional[float] = None
    soil_ph: Optional[confloat(ge=3, le=8)] = None

    # 접근성
    has_direct_road_access: bool = Field(..., description="도로 직접 접근 ✅ (쉼터 prereq)")
    distance_to_paved_road_m: Optional[float] = None

    # 위험
    in_disaster_zone: bool = Field(False, description="방재지구 (쉼터 제외 사유)")
    wildfire_risk_5km_mean: Optional[confloat(ge=0, le=1)] = None
    landslide_risk_5km_mean: Optional[confloat(ge=0, le=1)] = None

    # 출처
    source: str = Field(..., description="'iforest.nfcf.or.kr' | 'vworld' | 'byoa-dadream'")
    listing_url: Optional[str] = None
    contact_cooperative: Optional[str] = None


class ShimterCost(BaseModel):
    """M07 산촌체류형 쉼터 비용 시뮬레이션 (표준품셈 6항목 ±15%)."""
    foundation_won: int = Field(..., description="기초")
    main_structure_wood_33sqm_won: int = Field(..., description="목조 33㎡ 본체")
    deck_won: int = Field(..., description="데크")
    septic_tank_won: int = Field(..., description="정화조")
    driveway_won: int = Field(..., description="진입로")
    permit_won: int = Field(..., description="인허가")
    total_p10_won: int
    total_p50_won: int
    total_p90_won: int


class ShimterAssessment(BaseModel):
    """
    M07 7개 룰 검증 결과 (산지관리법 시행령 일부개정안).
    모든 7개 룰 통과 시 적합 → 비용 시뮬레이션 진행.
    """
    rule_sanji_area_400sqm_plus: bool       # 산지 ≥ 400㎡
    rule_site_under_100sqm: bool             # 부지 < 100㎡
    rule_floor_area_under_33sqm: bool        # 연면적 ≤ 33㎡
    rule_im_eob_yong_sanji: bool             # 임업용 산지
    rule_direct_road_access: bool            # 도로 직접 접근
    rule_outside_disaster_zone: bool         # 방재지구 외
    rule_no_fire_equipment: bool             # 화기 시설 불가

    is_eligible: bool
    cost_estimate: Optional[ShimterCost] = None
    recommended_design: Optional[str] = Field(
        None, description="권장 설계, 예: '33㎡ 목조 + 20㎡ 데크 + 정화조 + 주차장'"
    )
    next_step_guidance: str = Field(
        default="산지전용통합정보시스템 1644-0672 신청 절차 안내",
    )
    rule_violations: list[str] = Field(default_factory=list)


class LotMatch(BaseModel):
    """M07 최종 결과 — 사용자에게 보여지는 매물 카드."""
    lot: Lot
    suitability_for_target_product: confloat(ge=0, le=1)
    shimter_assessment: ShimterAssessment
    alternative_options: list[str] = Field(
        default_factory=list,
        description="쉼터 불가 시 대안, 예: '인근 농가 임차', '단지 내 숙소'",
    )
