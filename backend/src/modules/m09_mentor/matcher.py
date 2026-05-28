"""M09 — 시군 산림조합 + 산림사업법인 멘토 + 양성과정 + '이번 주 1번 액션'."""
from __future__ import annotations
import logging
from pathlib import Path
import json
logger = logging.getLogger(__name__)
_DATA = Path(__file__).parent.parent.parent.parent.parent / "data" / "processed"


async def find_mentors_and_cooperatives(
    sigungu_code: str,
    interested_product_codes: list[str] | None = None,
    include_education_courses: bool = True,
) -> dict:
    cooperatives_path = _DATA / "cooperatives_142.json"
    if cooperatives_path.exists():
        coops = json.loads(cooperatives_path.read_text(encoding="utf-8"))
        coop = next((c for c in coops if c.get("sigungu_code") == sigungu_code), None)
    else:
        coop = None
    if coop is None:
        coop = _fixture_coop(sigungu_code)
    return {
        "nearest_cooperative": coop,
        "top_mentors": _fixture_mentors(interested_product_codes or []),
        "nearest_education_courses": _fixture_courses() if include_education_courses else [],
        "this_week_action": "임업후계자 4월 1기 양성과정 신청 (마감 4/15, 40시간 비대면)",
        "confidence_score": 0.85,
    }


def _fixture_coop(sigungu_code: str) -> dict:
    return {
        "id": f"cooperative_{sigungu_code}",
        "name": "평창산림조합",
        "sigungu_code": sigungu_code,
        "address": "강원특별자치도 평창군 평창읍",
        "phone": "033-332-XXXX",
        "services": ["임업정책자금", "단기소득자금", "임야거래장터", "교육"],
        "available_loan_rates": {"sup_fillment": 1.0, "short_term_income": 2.0},
    }


def _fixture_mentors(product_codes: list[str]) -> list[dict]:
    return [
        {"id": "M_001", "name_initial": "박OO", "type": "individual_mentor",
         "sigungu_code": "4276", "specialty_product_codes": product_codes or ["P_001"],
         "years_experience": 18, "trust_score": 0.92,
         "contact_via": "평창산림조합 경유"},
        {"id": "M_002", "name_initial": "강원평창산림(주)", "type": "forest_business_corp",
         "sigungu_code": "4276", "specialty_product_codes": product_codes or ["P_001"],
         "trust_score": 0.85, "contact_via": "사업법인 직접"},
    ]


def _fixture_courses() -> list[dict]:
    from datetime import date
    return [
        {"course_id": "FHI_2026_1", "name": "2026년 임업후계자 양성과정 1기",
         "provider": "시니어공유경제연구원", "start_date": str(date(2026, 4, 15)),
         "end_date": str(date(2026, 4, 19)), "is_online": True, "hours_total": 40,
         "apply_deadline": str(date(2026, 4, 10)), "capacity": 50,
         "apply_url": "https://fhi.forest.go.kr"},
    ]
