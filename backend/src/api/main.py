"""
Soop Starter — FastAPI entrypoint.
WebSocket /chat = LLM 에이전트 streaming (5-state machine).
REST = 개별 모듈 호출 (디버그·시연용).
"""
from __future__ import annotations
import json
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ..core.config import settings
from ..core.cache import RedisCache
from ..agent.orchestrator import SoopAgentOrchestrator
from ..modules import (
    m01_profiling, m02_filter, m03_suitability, m05_income,
    m06_subsidy, m07_shimter, m08_forkg, m09_mentor, m10_disaster, m11_lifestyle,
)

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("soop")

redis: RedisCache | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis
    redis = RedisCache()
    if await redis.ping():
        logger.info("Redis connected")
    else:
        logger.warning("Redis unavailable; tool caching disabled")
    yield


app = FastAPI(
    title="Soop Starter Backend",
    version="0.1.0",
    description="한국 산촌 청년 임업인 진입 의사결정 지원 시스템 — Claude Opus 4.7 + 11 모듈",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Health / Meta
# ============================================================================
@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0", "model": settings.claude_model}


@app.get("/")
async def root():
    return {
        "service": "Soop Starter",
        "competition": "2026 산림 공공데이터·AI 활용 창업경진대회",
        "submission_deadline": "2026-06-19 18:00 KST",
        "modules": [f"M{i:02d}" for i in range(1, 12)],
        "docs": "/docs",
    }


# ============================================================================
# WebSocket /chat — 메인 시연 경로
# ============================================================================
@app.websocket("/chat")
async def chat_ws(ws: WebSocket):
    await ws.accept()
    session_id = str(uuid.uuid4())
    orchestrator = SoopAgentOrchestrator(session_id=session_id, redis=redis)
    logger.info(f"chat session {session_id} opened")

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)
            user_text = msg.get("text", "")
            if not user_text:
                continue

            async for chunk in orchestrator.chat_turn(user_text):
                await ws.send_text(json.dumps(chunk, ensure_ascii=False, default=str))
    except WebSocketDisconnect:
        logger.info(f"chat session {session_id} closed")
    except Exception as e:
        logger.exception(f"chat session {session_id} error")
        await ws.send_text(json.dumps({"type": "error", "message": str(e)}))


# ============================================================================
# REST debug endpoints — 개별 모듈 호출 (테스트·시연)
# ============================================================================
@app.post("/modules/m01/extract")
async def m01_extract(payload: dict):
    return await m01_profiling.extract_user_profile(**payload)


@app.post("/modules/m02/filter")
async def m02_filter_endpoint(payload: dict):
    return await m02_filter.filter_candidate_villages(**payload)


@app.post("/modules/m03/recommend")
async def m03_recommend(payload: dict):
    return await m03_suitability.recommend_forest_products(**payload)


@app.post("/modules/m05/simulate")
async def m05_simulate(payload: dict):
    return await m05_income.simulate_5year_income(**payload)


@app.post("/modules/m06/match")
async def m06_match(payload: dict):
    return await m06_subsidy.match_subsidies_timeline(**payload)


@app.post("/modules/m07/assess")
async def m07_assess(payload: dict):
    return await m07_shimter.assess_shimter_eligibility(**payload)


@app.post("/modules/m08/rag")
async def m08_rag(payload: dict):
    return await m08_forkg.answer_with_rag(**payload)


@app.post("/modules/m09/mentor")
async def m09_mentor_endpoint(payload: dict):
    return await m09_mentor.find_mentors_and_cooperatives(**payload)


@app.post("/modules/m10/alert")
async def m10_alert(payload: dict):
    return await m10_disaster.register_disaster_alert(**payload)


@app.post("/modules/m11/lifestyle")
async def m11_lifestyle_endpoint(payload: dict):
    return await m11_lifestyle.score_lifestyle_axes(**payload)


# ============================================================================
# Persona fixture endpoint — 시연 안정성 #2
# ============================================================================
@app.get("/persona/{persona_id}")
async def get_persona(persona_id: str):
    """P-01 ~ P-04 hard-coded fallback 반환. 발표 당일 API 장애 대비."""
    from pathlib import Path
    fixture_path = Path(__file__).parent.parent.parent.parent / "data" / "fixtures" / f"persona_{persona_id.lower()}.json"
    if not fixture_path.exists():
        raise HTTPException(404, f"persona {persona_id} fixture not found")
    return JSONResponse(json.loads(fixture_path.read_text(encoding="utf-8")))
