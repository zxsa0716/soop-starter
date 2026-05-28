"""
Soop Starter — 5-state Machine LLM Agent Orchestrator
=====================================================
Claude Opus 4.7 + function calling. 11 모듈을 사용자 입력에 따라 자동 dispatch.

5 states:
    1. Profiling  → M01
    2. Narrowing  → M02 + M11 (병렬)
    3. Matching   → M03 + M04
    4. Decision   → M05 + M06 + M07 + M09
    5. Free Q&A   → M08 (background: M10)

Latency 목표: 첫 토큰 ≤ 2초, 전체 ≤ 15초.
"""
from __future__ import annotations
import asyncio
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator

import anthropic
from anthropic.types import MessageParam

from ..core.config import settings
from ..core.cache import RedisCache
from ..modules import (
    m01_profiling, m02_filter, m03_suitability, m04_similarity,
    m05_income, m06_subsidy, m07_shimter, m08_forkg,
    m09_mentor, m10_disaster, m11_lifestyle,
)

logger = logging.getLogger(__name__)

# ============================================================================
# State
# ============================================================================
class AgentState(str, Enum):
    PROFILING = "profiling"
    NARROWING = "narrowing"
    MATCHING = "matching"
    DECISION = "decision"
    FREE_QA = "free_qa"


# ============================================================================
# Dispatch table — function_schemas.json `name` → 실제 호출
# ============================================================================
TOOL_DISPATCH = {
    "extract_user_profile":           m01_profiling.extract_user_profile,
    "filter_candidate_villages":      m02_filter.filter_candidate_villages,
    "recommend_forest_products":      m03_suitability.recommend_forest_products,
    "find_similar_villages":          m04_similarity.find_similar_villages,
    "simulate_5year_income":          m05_income.simulate_5year_income,
    "match_subsidies_timeline":       m06_subsidy.match_subsidies_timeline,
    "assess_shimter_eligibility":     m07_shimter.assess_shimter_eligibility,
    "answer_with_rag":                m08_forkg.answer_with_rag,
    "find_mentors_and_cooperatives":  m09_mentor.find_mentors_and_cooperatives,
    "register_disaster_alert":        m10_disaster.register_disaster_alert,
    "score_lifestyle_axes":           m11_lifestyle.score_lifestyle_axes,
}

# ============================================================================
# Asset loading
# ============================================================================
_AGENT_DIR = Path(__file__).parent
SYSTEM_PROMPT = (_AGENT_DIR / "system_prompt.md").read_text(encoding="utf-8")
FUNCTION_SCHEMAS = json.loads(
    (_AGENT_DIR / "function_schemas.json").read_text(encoding="utf-8")
)


def _to_anthropic_tools(schema_doc: dict) -> list[dict]:
    """function_schemas.json → Anthropic tools array."""
    return [
        {
            "name": t["name"],
            "description": t["description"],
            "input_schema": t["input_schema"],
        }
        for t in schema_doc["tools"]
    ]


ANTHROPIC_TOOLS = _to_anthropic_tools(FUNCTION_SCHEMAS)


# ============================================================================
# Orchestrator
# ============================================================================
class SoopAgentOrchestrator:
    """단일 사용자 세션 단위 오케스트레이터."""

    def __init__(self, session_id: str, redis: RedisCache | None = None):
        self.session_id = session_id
        self.state: AgentState = AgentState.PROFILING
        self.messages: list[MessageParam] = []
        self.user_profile: dict | None = None
        self.candidate_villages: list[dict] = []
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.redis = redis

    async def chat_turn(self, user_text: str) -> AsyncIterator[dict]:
        """단일 사용자 input 처리. SSE/WebSocket으로 chunk stream."""
        self.messages.append({"role": "user", "content": user_text})

        # --- Claude 호출 with tool use ---
        for _ in range(8):  # max 8 tool-use round
            response = await self.client.messages.create(
                model=settings.claude_model,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=ANTHROPIC_TOOLS,
                messages=self.messages,
                stream=False,  # MVP: 첫 구현은 non-stream, 추후 stream으로 첫 토큰 ≤ 2초 보장
            )

            self.messages.append({"role": "assistant", "content": response.content})

            tool_uses = [b for b in response.content if b.type == "tool_use"]
            if not tool_uses:
                # 일반 텍스트 응답 — 사용자에게 stream
                for block in response.content:
                    if block.type == "text":
                        yield {"type": "text", "delta": block.text}
                yield {"type": "done", "state": self.state.value}
                return

            # --- Tool dispatch (병렬) ---
            tool_results = await asyncio.gather(
                *[self._dispatch_tool(tu) for tu in tool_uses]
            )

            self.messages.append({
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tu.id,
                        "content": json.dumps(result, default=str, ensure_ascii=False),
                    }
                    for tu, result in zip(tool_uses, tool_results)
                ],
            })

            for tu, result in zip(tool_uses, tool_results):
                yield {
                    "type": "tool_result",
                    "name": tu.name,
                    "module": _module_id(tu.name),
                    "summary": _summarize_result(tu.name, result),
                }
                self._update_state(tu.name, result)

        yield {"type": "error", "message": "Max tool-use rounds exceeded"}

    async def _dispatch_tool(self, tool_use) -> dict:
        """Function dispatch + Redis 캐시 + fallback to persona fixture."""
        fn = TOOL_DISPATCH.get(tool_use.name)
        if fn is None:
            return {"error": f"unknown tool: {tool_use.name}"}

        cache_key = f"tool:{tool_use.name}:{hash(json.dumps(tool_use.input, sort_keys=True, default=str))}"
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                logger.info(f"cache HIT: {tool_use.name}")
                return cached

        try:
            result = await fn(**tool_use.input)
        except Exception as e:
            logger.exception(f"tool {tool_use.name} failed; falling back to fixture")
            result = _fallback_fixture(tool_use.name, tool_use.input)

        if self.redis:
            await self.redis.set(cache_key, result, ttl=settings.redis_ttl_seconds)
        return result

    def _update_state(self, tool_name: str, result: dict) -> None:
        """간단한 state 전이 로직 (실측 호출에 따라 확장)."""
        if tool_name == "extract_user_profile":
            self.user_profile = result
            self.state = AgentState.NARROWING
        elif tool_name == "filter_candidate_villages":
            self.candidate_villages = result.get("villages", [])
            self.state = AgentState.MATCHING
        elif tool_name in {"recommend_forest_products", "find_similar_villages"}:
            self.state = AgentState.DECISION
        elif tool_name == "answer_with_rag":
            self.state = AgentState.FREE_QA


# ============================================================================
# Helpers
# ============================================================================
_NAME_TO_MODULE = {
    "extract_user_profile": "M01", "filter_candidate_villages": "M02",
    "recommend_forest_products": "M03", "find_similar_villages": "M04",
    "simulate_5year_income": "M05", "match_subsidies_timeline": "M06",
    "assess_shimter_eligibility": "M07", "answer_with_rag": "M08",
    "find_mentors_and_cooperatives": "M09", "register_disaster_alert": "M10",
    "score_lifestyle_axes": "M11",
}

def _module_id(tool_name: str) -> str:
    return _NAME_TO_MODULE.get(tool_name, "UNKNOWN")


def _summarize_result(tool_name: str, result: dict) -> str:
    """UI 카드용 간단 요약."""
    if tool_name == "filter_candidate_villages":
        n = len(result.get("villages", []))
        return f"466 산촌 → {n} 후보로 좁힘"
    if tool_name == "recommend_forest_products":
        n = len(result.get("recommendations", []))
        return f"Top-{n} 임산물 추천 + SHAP"
    if tool_name == "simulate_5year_income":
        p50 = result.get("cumulative_5y_p50_won", 0)
        return f"5년 누적 P50 {p50/100_000_000:.2f}억"
    return f"{tool_name} 완료"


def _fallback_fixture(tool_name: str, inputs: dict) -> dict:
    """4 페르소나 hard-coded fixture로 fallback (시연 안정성 3중 안전장치 중 #2)."""
    fixtures_dir = Path(__file__).parent.parent.parent.parent / "data" / "fixtures"
    for persona_id in ["p01", "p02", "p03", "p04"]:
        fixture_path = fixtures_dir / f"persona_{persona_id}.json"
        if fixture_path.exists():
            data = json.loads(fixture_path.read_text(encoding="utf-8"))
            module_results = data.get("module_results", {})
            if tool_name in module_results:
                logger.warning(f"using fallback fixture: {persona_id} for {tool_name}")
                return module_results[tool_name]
    return {"error": f"fallback fixture missing for {tool_name}"}
