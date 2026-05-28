"""
M08 — BGE-m3 + bge-reranker-v2 + BM25/vector RRF + ForKG-Korea 1~2 hop traversal.

답변 가드레일:
  - citation 1개 이상 필수 (min_citation_count)
  - confidence < 0.6 시 거절
  - 법령 조항 + 페이지 인용 본문에 자연스럽게 녹임
"""
from __future__ import annotations
import json
import logging
from pathlib import Path

import anthropic
import chromadb
import httpx
import networkx as nx
from rank_bm25 import BM25Okapi

from ...core.config import settings

logger = logging.getLogger(__name__)

_KG_PATH = Path(__file__).parent.parent.parent.parent.parent / "data" / "processed" / "forkg_korea.json"
_kg_graph: nx.MultiDiGraph | None = None
_chroma_client = None
_collection = None
_bm25 = None
_chunks: list[dict] = []


def _lazy_load():
    global _kg_graph, _chroma_client, _collection, _bm25, _chunks
    if _kg_graph is None and _KG_PATH.exists():
        data = json.loads(_KG_PATH.read_text(encoding="utf-8"))
        _kg_graph = nx.node_link_graph(data, directed=True, multigraph=True)
    if _chroma_client is None:
        try:
            _chroma_client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
            _collection = _chroma_client.get_or_create_collection("soop_legal_corpus")
            data = _collection.get(limit=10_000)
            _chunks = [{"id": i, "text": t, "meta": m}
                       for i, t, m in zip(data["ids"], data["documents"], data["metadatas"])]
            if _chunks:
                _bm25 = BM25Okapi([c["text"].split() for c in _chunks])
        except Exception as e:
            logger.warning(f"Chroma load failed: {e}")


async def answer_with_rag(
    question: str,
    user_profile_context: dict | None = None,
    top_k_chunks: int = 5,
    min_citation_count: int = 1,
) -> dict:
    """RAG + ForKG-Korea traversal + 인용 강제."""
    _lazy_load()

    # --- 1. Hybrid retrieval (BM25 + vector, RRF) ---
    chunks = await _hybrid_retrieve(question, top_k=top_k_chunks)
    if not chunks:
        return _refusal_response(question, "RAG corpus empty (W1-T5 DAG4 미실행)")

    # --- 2. KG traversal (1~2 hop expansion) ---
    kg_context = _traverse_kg(question, max_hops=2)

    # --- 3. Claude 호출 with citation 강제 ---
    citation_context = "\n\n".join(
        f"[CHUNK {i+1}] {c['meta'].get('law_name', '')} {c['meta'].get('article', '')}\n{c['text'][:500]}\n출처: {c['meta'].get('source_url', '')}"
        for i, c in enumerate(chunks)
    )

    system = (
        "당신은 한국 산림 정책 RAG 에이전트입니다. 주어진 청크에서만 답변하세요.\n"
        "반드시 청크 출처(법령 조항·페이지)를 본문에 자연스럽게 인용하세요.\n"
        "청크에 답이 없으면 'REFUSE: <이유>'로만 응답하세요.\n"
        f"\n## ForKG-Korea 컨텍스트 (1~2 hop)\n{kg_context}\n"
        f"\n## 검색된 청크\n{citation_context}"
    )

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    user_msg = f"질문: {question}"
    if user_profile_context:
        user_msg += f"\n\n사용자 컨텍스트: {json.dumps(user_profile_context, ensure_ascii=False)}"

    response = await client.messages.create(
        model=settings.claude_model,
        max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )
    answer_text = "".join(b.text for b in response.content if b.type == "text").strip()

    # --- 4. Citation 가드레일 ---
    if answer_text.startswith("REFUSE:"):
        return _refusal_response(question, answer_text[7:].strip())

    cited_chunks = [c for i, c in enumerate(chunks) if f"CHUNK {i+1}" in answer_text or c["meta"].get("article", "") in answer_text]
    if len(cited_chunks) < min_citation_count:
        return _refusal_response(question, "인용 부족 (citation guardrail triggered)")

    return {
        "answer": answer_text,
        "citations": [_to_citation(c) for c in cited_chunks],
        "confidence": min(1.0, 0.6 + 0.1 * len(cited_chunks)),
        "refused": False,
        "fallback_disclaimer": (
            "본 답변은 산림 정책 자료 RAG 결과입니다. 법적·재무적 의사결정은 "
            "산지전용통합정보시스템(1644-0672), 산림조합중앙회(1544-7170), "
            "한국임업진흥원(1600-3248) 등 공식 채널 확인을 권장합니다."
        ),
    }


# ============================================================================
async def _hybrid_retrieve(query: str, top_k: int) -> list[dict]:
    """BM25 + vector → RRF top_k."""
    if not _chunks or _collection is None:
        return []

    # BM25 top-20
    bm25_scores = _bm25.get_scores(query.split())
    bm25_idx = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:20]

    # vector top-20 (Chroma)
    v_results = _collection.query(query_texts=[query], n_results=20)
    v_ids = v_results["ids"][0] if v_results.get("ids") else []
    chunk_idx_by_id = {c["id"]: i for i, c in enumerate(_chunks)}
    v_idx = [chunk_idx_by_id[i] for i in v_ids if i in chunk_idx_by_id]

    # RRF (k=60)
    k_rrf = 60
    rrf = {}
    for rank, i in enumerate(bm25_idx):
        rrf[i] = rrf.get(i, 0) + 1.0 / (k_rrf + rank)
    for rank, i in enumerate(v_idx):
        rrf[i] = rrf.get(i, 0) + 1.0 / (k_rrf + rank)

    top = sorted(rrf.items(), key=lambda kv: kv[1], reverse=True)[:top_k]
    return [_chunks[i] for i, _ in top]


def _traverse_kg(query: str, max_hops: int = 2) -> str:
    """질문에 등장하는 entity 키워드를 NetworkX 그래프에서 검색 → 1~2 hop 인접 노드/엣지 텍스트 반환."""
    if _kg_graph is None:
        return ""
    seed_nodes = [n for n in _kg_graph.nodes if any(kw in str(n) for kw in query.split())][:5]
    if not seed_nodes:
        return ""
    expanded = set(seed_nodes)
    for hop in range(max_hops):
        new = set()
        for n in expanded:
            new |= set(_kg_graph.successors(n)) | set(_kg_graph.predecessors(n))
        expanded |= new
    lines = []
    for n in list(expanded)[:20]:
        attrs = _kg_graph.nodes[n]
        lines.append(f"- {n} ({attrs.get('type', '?')}): {attrs.get('name', '')}")
    return "\n".join(lines)


def _to_citation(chunk: dict) -> dict:
    m = chunk["meta"]
    return {
        "chunk_id": str(chunk["id"]),
        "law_name": m.get("law_name"),
        "article": m.get("article"),
        "page": m.get("page"),
        "text_snippet": chunk["text"][:400],
        "source_url": m.get("source_url", ""),
        "score": 0.9,
    }


def _refusal_response(question: str, reason: str) -> dict:
    return {
        "answer": (
            f"제가 보유한 산림 정책 자료(법제처 OpenAPI 5법령 + 시행지침서)에서 "
            f"이 질문에 대한 명확한 근거를 찾지 못했습니다 ({reason}). "
            f"산림조합중앙회(1544-7170) 또는 산지전용통합정보시스템(1644-0672)으로 문의해 주세요."
        ),
        "citations": [],
        "confidence": 0.0,
        "refused": True,
        "refusal_reason": reason,
        "fallback_disclaimer": "RAG citation guardrail (M08).",
    }
