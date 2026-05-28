"""
M08 — ForKG-Korea + RAG.
"""
from typing import Optional, Literal
from pydantic import BaseModel, Field, confloat


class EntityRef(BaseModel):
    """ForKG-Korea entity 참조 (9 클래스 중 하나)."""
    id: str = Field(..., description="UUID 또는 stable hash")
    type: Literal[
        "Location", "ForestProduct", "Policy", "Subsidy",
        "Organization", "Person", "Procedure", "LegalProvision", "DataSource",
    ]
    name: str
    metadata: dict = Field(default_factory=dict)


class RelationEdge(BaseModel):
    """ForKG-Korea relation (11 클래스 중 하나)."""
    src: EntityRef
    dst: EntityRef
    type: Literal[
        "SUITABLE_FOR", "GOVERNED_BY", "PROVIDES", "LOCATED_IN", "ELIGIBLE_FOR",
        "SPECIALIZES_IN", "REQUIRES", "AMENDED_BY", "APPLIES_TO", "SOURCED_FROM",
        "ADJACENT_TO",
    ]
    properties: dict = Field(default_factory=dict)
    confidence: confloat(ge=0, le=1) = 1.0


class GraphQueryResult(BaseModel):
    """1~2 hop traversal 결과."""
    seed_entities: list[EntityRef]
    expanded_entities: list[EntityRef]
    edges: list[RelationEdge]
    context_text: str = Field(..., description="LLM 컨텍스트 주입용 직렬화")


class Citation(BaseModel):
    """답변에 강제 첨부되는 인용. 미달 시 답변 거절 가드레일."""
    chunk_id: str
    law_name: Optional[str] = None
    article: Optional[str] = None
    page: Optional[int] = None
    text_snippet: str = Field(..., max_length=400)
    source_url: str
    score: confloat(ge=0, le=1)


class CitedAnswer(BaseModel):
    """M08 RAG 최종 답변."""
    answer: str
    citations: list[Citation] = Field(..., min_length=1)
    confidence: confloat(ge=0, le=1)
    refused: bool = False
    refusal_reason: Optional[str] = None
    fallback_disclaimer: str = Field(
        default=(
            "본 답변은 산림 정책 자료 RAG 결과입니다. 법적·재무적 의사결정은 "
            "산지전용통합정보시스템(1644-0672), 산림조합중앙회(1544-7170), "
            "한국임업진흥원(1600-3248) 등 공식 채널 확인을 권장합니다."
        )
    )
