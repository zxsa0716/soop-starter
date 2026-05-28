"""
M01 사용자 프로파일링 결과 — 27 결정 변수.
3턴 max + 자연어/슬라이더 hybrid (박지영 위원 강제 사항).
"""
from __future__ import annotations
from datetime import date
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field, conint, confloat


# ============================================================================
# Enums — 결정 변수 카테고리
# ============================================================================
class TransitionType(str, Enum):
    weekend_farming = "주말농장형"        # P-01 김도현
    gradual_5y = "점진적 5년 전환"        # P-01, P-03
    immediate = "즉시 전환"                # P-04
    pre_retirement = "퇴직 후 전환"        # P-03
    learning_first = "학습 우선"           # P-02


class RiskAppetite(str, Enum):
    conservative = "보수적"
    moderate = "중도적"
    aggressive = "공격적"


class FarmExperience(str, Enum):
    none = "없음"
    hobby = "취미 수준"
    seasonal = "계절 도움"
    side_business = "부업"
    professional = "전업"


class LifestylePreference(str, Enum):
    hiking = "등산"
    healing = "치유"
    leisure = "휴양"
    nature = "자연 접근"


# ============================================================================
# Sub-models
# ============================================================================
class ProfileTurn(BaseModel):
    """M01 3턴 인터뷰 단일 turn 기록."""
    turn_no: conint(ge=1, le=3)
    role: Literal["user", "assistant"]
    text: str
    extracted_fields: list[str] = Field(default_factory=list)


# ============================================================================
# Main schema — UserProfile (27 결정 변수)
# ============================================================================
class UserProfile(BaseModel):
    """
    M01 산출물. 11 모듈 오케스트레이션의 root payload.

    27 fields: 인구학(2) + 자원(2) + 경험·기술(2) + 라이프스타일(3)
              + 임업 선호(3) + 자산(3) + 목표(2) + 자격(4) + 기타(6)
    """
    # --- 인구학 (2) ---
    age: conint(ge=18, le=80) = Field(..., description="만 나이")
    family_size: conint(ge=1, le=10) = Field(..., description="가족 구성원 수 (본인 포함)")

    # --- 자원 (2) ---
    capital_won: conint(ge=0) = Field(..., description="가용 자본 (원)")
    monthly_required_income_won: conint(ge=0) = Field(
        ..., description="월 필요 소득 (원). 임업 외 소득과 합산하여 가계 안정성 평가"
    )

    # --- 경험·기술 (2) ---
    farm_experience: FarmExperience = FarmExperience.none
    technical_skills: list[str] = Field(
        default_factory=list,
        description='예: ["원격근무", "데이터분석", "마케팅"]',
    )

    # --- 라이프스타일 (3) ---
    transition_type: TransitionType
    region_preferences: list[str] = Field(
        default_factory=list,
        description='예: ["강원도", "경북북부"]. 빈 list면 전국',
    )
    max_distance_from_seoul_km: Optional[conint(ge=0, le=500)] = Field(
        None, description="서울 거리 제약 (km). None이면 무제한"
    )
    lifestyle_preferences: list[LifestylePreference] = Field(
        default_factory=list,
        description="박지영 위원 강조 — 청년 도시민 1차 동기는 자연 가까이",
    )

    # --- 임업 선호 (3) ---
    interested_products: list[str] = Field(
        default_factory=list, description='예: ["표고", "산양삼"]. 비어있으면 추천 자유'
    )
    risk_appetite: RiskAppetite = RiskAppetite.moderate
    planning_horizon_years: conint(ge=1, le=10) = 5

    # --- 자산 (3) ---
    inherited_lot_pnu: Optional[str] = Field(
        None, description="상속 임야 PNU (19자리). 있으면 BYOA M07 직결 (P-03)"
    )
    inherited_lot_area_ha: Optional[confloat(ge=0)] = None
    own_house_in_target_region: bool = False

    # --- 목표 (2) ---
    primary_goal: str = Field(..., description="자유 텍스트, 예: '주말농장으로 시작'")
    secondary_goals: list[str] = Field(default_factory=list)

    # --- 자격 (4) — 보조사업 매칭 룰 직결 ---
    available_for_40h_training: bool = Field(
        True, description="임업후계자 40시간 교육 (4월/10월 비대면 1기 가능)"
    )
    eligible_for_young_subsidy: bool = Field(
        False, description="만 18~40세 자동 계산 (M06에서 검증)"
    )
    sigungu_residence: Optional[str] = Field(
        None, description="현재 거주 시군 — 시군 정착지원금 자격"
    )
    plans_to_register_business: bool = True

    # --- 기타 (6) ---
    has_existing_loans: bool = False
    spouse_support_level: Literal["full", "partial", "none"] = "partial"
    remote_work_eligible: bool = False
    target_start_date: Optional[date] = None
    contact_phone: Optional[str] = Field(None, description="알림 동의 시만, M10 push용")
    contact_email: Optional[str] = None

    # --- 메타 ---
    interview_turns: list[ProfileTurn] = Field(default_factory=list)
    completeness_score: confloat(ge=0, le=1) = Field(
        0.0, description="27 fields 중 채워진 비율 (target ≥ 0.63 = 17/27)"
    )

    def is_complete_enough(self) -> bool:
        """3턴 인터뷰 완료율 70% (박지영 위원 목표)."""
        return self.completeness_score >= 0.63
