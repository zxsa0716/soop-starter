"""
M09 — 멘토 · 산림조합 · 양성과정 매칭.
nfcf.or.kr robots.txt 준수 크롤 → 142 시군 1:1 매핑.
"""
from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, Field, confloat, conint


class Cooperative(BaseModel):
    """산림조합 142개 (산림조합중앙회 nfcf.or.kr)."""
    id: str = Field(..., description="cooperative_<sigungu_code>")
    name: str = Field(..., description="예: '평창산림조합'")
    sigungu_code: str
    address: str
    phone: str = Field(..., description="예: '033-332-XXXX'")
    services: list[str] = Field(
        default_factory=list,
        description="예: ['임업정책자금', '단기소득자금', '임야거래장터', '교육']",
    )
    available_loan_rates: Optional[dict[str, float]] = Field(
        None, description="{'sup-fillment': 1.0, 'short-term-income': 2.0} (%)"
    )


class Mentor(BaseModel):
    """
    멘토 (산림사업법인 OpenAPI + 산림형 예비사회적 기업 + 익명화 사례).
    개인정보 보호 — 이름은 이니셜만.
    """
    id: str
    name_initial: str = Field(..., description="예: '박OO'")
    type: Literal["forest_business_corp", "social_enterprise", "individual_mentor"]
    sigungu_code: str
    specialty_product_codes: list[str] = Field(
        default_factory=list, description="전문 임산물 코드 list"
    )
    years_experience: Optional[conint(ge=0)] = None
    trust_score: confloat(ge=0, le=1) = Field(
        ..., description="산림사업법인 기술능력 등급 + 상벌 기록 기반"
    )
    contact_via: str = Field(default="산림조합 경유 + 교육과정 직접 연결")


class EducationCourse(BaseModel):
    """산림교육원 임업후계자 양성과정 (fhi.forest.go.kr)."""
    course_id: str
    name: str = Field(..., description="예: '2026년 임업후계자 양성과정 1기'")
    provider: str = Field(..., description="예: '시니어공유경제연구원', '산림교육원'")
    start_date: date
    end_date: date
    is_online: bool = True
    hours_total: conint(ge=1) = 40
    apply_deadline: Optional[date] = None
    capacity: Optional[int] = None
    apply_url: Optional[str] = None


class MentorBundle(BaseModel):
    """M09 출력 — '이번 주 1번 액션' 형식 우선."""
    nearest_cooperative: Cooperative
    top_mentors: list[Mentor] = Field(..., max_length=3)
    nearest_education_courses: list[EducationCourse] = Field(..., max_length=2)
    this_week_action: str = Field(
        ..., description="예: '임업후계자 4월 1기 신청 (마감 4/15)'"
    )
    confidence_score: confloat(ge=0, le=1)
