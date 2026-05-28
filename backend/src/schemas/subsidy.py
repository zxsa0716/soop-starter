"""
M06 — 보조사업 매칭 + 5년 timeline.
"김재현 위원 요구: list 아닌 5년 timeline 출력"
"""
from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, Field, conint


class Subsidy(BaseModel):
    """~30 보조사업 카탈로그 (산림 미래혁신센터 90억, 영양 105억, 임업직불금 등)."""
    code: str
    name: str
    agency: str = Field(..., description="예: '산림청', '한국임업진흥원', '평창군'")
    parent_policy: Optional[str] = None
    is_2026_new: bool = False

    # 금액
    amount_won: Optional[int] = None
    amount_formula: Optional[str] = None

    # 자격 룰 (1단계 룰 엔진)
    eligibility_age_min: Optional[int] = None
    eligibility_age_max: Optional[int] = None
    eligibility_area_ha_min: Optional[float] = None
    eligibility_region: list[str] = Field(default_factory=list)
    eligibility_requires_business_registration: bool = False
    eligibility_requires_40h_training: bool = False
    eligibility_other_rules: list[str] = Field(default_factory=list)

    # 신청
    apply_period: Optional[str] = Field(None, description="예: '매년 3~5월'")
    apply_url: Optional[str] = None
    apply_method: str = Field(default="온라인 + 시군 산림과 방문")

    # RAG citation (2단계 LLM verification)
    cite_law: Optional[str] = None
    cite_guideline_url: Optional[str] = None


class ActionTimelineStep(BaseModel):
    """5년 timeline의 단일 step."""
    year: conint(ge=1, le=5)
    month: Optional[conint(ge=1, le=12)] = None
    quarter: Optional[Literal["Q1", "Q2", "Q3", "Q4"]] = None
    title: str = Field(..., description="예: '임업후계자 4월 1기 교육 신청'")
    description: str
    related_subsidy_code: Optional[str] = None
    deliverable: Optional[str] = Field(None, description="예: '경영체 등록증 PDF'")
    deadline: Optional[date] = None
    is_this_week_action: bool = Field(False, description="시연 강조용 — '이번 주 1번 액션'")


class SubsidyMatch(BaseModel):
    """M06 출력 — 5년 timeline 통합."""
    matched_subsidies: list[Subsidy]
    timeline: list[ActionTimelineStep]
    this_week_top_action: ActionTimelineStep = Field(
        ..., description="이번 주 1번 액션 (M09 출력과 통합)"
    )
    total_expected_subsidy_5y_won: int
    rule_verification_summary: dict[str, list[str]] = Field(
        default_factory=dict, description="{'satisfied': [...], 'violated': [...]}"
    )
