"""M01 — Claude few-shot로 자연어 단락에서 27 결정 변수 추출."""
from __future__ import annotations
import json
import logging
from pathlib import Path

import anthropic

from ...core.config import settings
from ...schemas import UserProfile, ProfileTurn

logger = logging.getLogger(__name__)

_PROMPT_PATH = Path(__file__).parent / "extraction_prompt.md"
EXTRACTION_PROMPT = _PROMPT_PATH.read_text(encoding="utf-8") if _PROMPT_PATH.exists() else ""


async def extract_user_profile(
    raw_text: str,
    previous_turns: list[dict] | None = None,
    form_overrides: dict | None = None,
) -> dict:
    """
    Claude Opus 4.7로 자연어에서 UserProfile 27 fields 추출.

    Returns:
        dict — UserProfile.model_dump() + 'completeness_score' + 'turn_no'
    """
    previous_turns = previous_turns or []
    form_overrides = form_overrides or {}
    turn_no = len(previous_turns) + 1

    # --- Claude 호출 ---
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    schema_hint = json.dumps(UserProfile.model_json_schema(), ensure_ascii=False, indent=2)
    system = (
        EXTRACTION_PROMPT
        + "\n\n## Pydantic schema (target output)\n```json\n"
        + schema_hint
        + "\n```\n"
        + "추출한 fields만 JSON으로 응답하세요. 모르는 필드는 null로 두세요."
    )
    user_msg = (
        f"## Turn {turn_no} 사용자 입력\n{raw_text}\n\n"
        f"## 이전 turn 누적 fields (수정 가능)\n{json.dumps(_aggregate_prior(previous_turns), ensure_ascii=False, indent=2)}\n\n"
        f"## Form overrides (사용자 슬라이더 수정)\n{json.dumps(form_overrides, ensure_ascii=False, indent=2)}"
    )

    response = await client.messages.create(
        model=settings.claude_model,
        max_tokens=2048,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )

    text = "".join(b.text for b in response.content if b.type == "text")
    try:
        extracted = _parse_json_block(text)
    except Exception as e:
        logger.warning(f"M01 JSON parse failed: {e}; returning partial")
        extracted = {}

    extracted.update(form_overrides)
    extracted["interview_turns"] = previous_turns + [
        {"turn_no": turn_no, "role": "user", "text": raw_text, "extracted_fields": list(extracted.keys())}
    ]
    extracted["completeness_score"] = _calc_completeness(extracted)
    return extracted


# ============================================================================
# Helpers
# ============================================================================
def _aggregate_prior(prior_turns: list[dict]) -> dict:
    out: dict = {}
    for t in prior_turns:
        if t.get("role") == "extracted":
            out.update(t.get("fields", {}))
    return out


def _parse_json_block(text: str) -> dict:
    """Claude 응답에서 첫 ```json ... ``` 블록 또는 가장 큰 {} 객체 파싱."""
    if "```json" in text:
        chunk = text.split("```json", 1)[1].split("```", 1)[0]
        return json.loads(chunk)
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start : end + 1])


_REQUIRED_FIELDS = {
    "age", "family_size", "capital_won", "monthly_required_income_won",
    "farm_experience", "transition_type", "interested_products", "risk_appetite",
    "planning_horizon_years", "primary_goal",
}
# 27 fields 중 'must-have' 10개 — 17/27 미만이면 3턴째에서 추가 질문
_TOTAL_FIELDS_COUNT = 27


def _calc_completeness(extracted: dict) -> float:
    filled = sum(1 for k, v in extracted.items() if v not in (None, "", [], {}))
    return min(filled / _TOTAL_FIELDS_COUNT, 1.0)
