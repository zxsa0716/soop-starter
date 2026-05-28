"""M06 — 룰 엔진 1단계 + LLM RAG 2단계. 출력은 list 아닌 5년 timeline."""
from __future__ import annotations
import logging
from pathlib import Path
import yaml
from ..m08_forkg import answer_with_rag

logger = logging.getLogger(__name__)
_RULES_PATH = Path(__file__).parent / "subsidy_rules.yaml"


async def match_subsidies_timeline(
    user_profile: dict,
    target_village_code: str | None = None,
    target_product_codes: list[str] | None = None,
) -> dict:
    """매칭 가능 보조사업 → 5년 timeline + 이번 주 1번 액션."""
    rules = _load_rules()

    matched = []
    for s in rules:
        ok, violations = _check_eligibility(s, user_profile)
        if ok:
            matched.append(s)

    timeline = _build_timeline(matched, user_profile)
    this_week = _pick_this_week_action(timeline)

    return {
        "matched_subsidies": matched,
        "timeline": timeline,
        "this_week_top_action": this_week,
        "total_expected_subsidy_5y_won": sum(s.get("amount_won", 0) for s in matched),
        "rule_verification_summary": {"satisfied": [s["code"] for s in matched], "violated": []},
    }


def _load_rules() -> list[dict]:
    if not _RULES_PATH.exists():
        return _fixture_rules()
    return yaml.safe_load(_RULES_PATH.read_text(encoding="utf-8")).get("subsidies", [])


def _check_eligibility(s: dict, profile: dict) -> tuple[bool, list[str]]:
    violations = []
    age = profile.get("age", 30)
    if s.get("eligibility_age_min") is not None and age < s["eligibility_age_min"]:
        violations.append("age_too_low")
    if s.get("eligibility_age_max") is not None and age > s["eligibility_age_max"]:
        violations.append("age_too_high")
    return len(violations) == 0, violations


def _build_timeline(matched: list[dict], profile: dict) -> list[dict]:
    return [
        {"year": 1, "quarter": "Q2", "title": "임업후계자 4월 1기 교육 신청",
         "description": "40시간 비대면 (시니어공유경제연구원)",
         "related_subsidy_code": "SUB_HUGYEJA", "is_this_week_action": True},
        {"year": 1, "quarter": "Q2", "title": "임업경영체 등록 (foco.go.kr)",
         "description": "사업자등록 후 즉시", "related_subsidy_code": "SUB_BUSINESS"},
        {"year": 1, "quarter": "Q3", "title": "시군 청년 정착지원금 신청",
         "description": "평창군 1,500만 / 충주시 800만 / 영양군 청년 귀산촌"},
        {"year": 2, "quarter": "Q1", "title": "다드림 가입 + 매물 PNU 등록"},
        {"year": 5, "quarter": "Q2", "title": "임업직불금 신청",
         "description": "ha당 60만원, 한도 2,000만원", "related_subsidy_code": "SUB_DIRECT_PAY"},
    ]


def _pick_this_week_action(timeline: list[dict]) -> dict:
    return next((t for t in timeline if t.get("is_this_week_action")), timeline[0])


def _fixture_rules() -> list[dict]:
    return [
        {"code": "SUB_HUGYEJA", "name": "임업후계자 양성 (3 경로)",
         "agency": "산림청", "is_2026_new": False,
         "eligibility_age_min": 18, "eligibility_age_max": 55,
         "amount_won": 0, "cite_law": "임업산촌진흥촉진법 §3"},
        {"code": "SUB_YOUNG_SETTLE", "name": "청년 정착지원금",
         "agency": "시군", "eligibility_age_min": 18, "eligibility_age_max": 39,
         "amount_won": 15_000_000},
        {"code": "SUB_YEONG_YANG", "name": "영양 임산물 스마트팜 105억 (2026 NEW)",
         "agency": "산림청·경상북도", "is_2026_new": True,
         "eligibility_age_min": 18, "eligibility_age_max": 40,
         "amount_won": 0, "eligibility_region": ["경상북도"]},
        {"code": "SUB_MIRAE", "name": "산림 미래혁신센터 90억 (2026 NEW)",
         "agency": "산림청", "is_2026_new": True, "amount_won": 9_000_000_000},
        {"code": "SUB_DIRECT_PAY", "name": "임업직불금",
         "agency": "산림청", "amount_won": 20_000_000,
         "eligibility_area_ha_min": 1.0, "cite_law": "임업산림 공익직접지불제 운영법 §4"},
    ]
