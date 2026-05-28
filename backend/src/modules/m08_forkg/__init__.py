"""
M08 ForKG-Korea + RAG (★ 학술 contribution #1)
==============================================
ForPKG-1.0 framework (Sun & Luo, arXiv:2411.11090) 한국 first application.

Components:
  - ontology.yaml — 9 entity × 11 relation (data/ontology/forkg_korea_ontology.yaml)
  - NetworkX in-memory + JSON 직렬화 (Neo4j 격하)
  - Chroma 벡터 DB (3,000 청크 임베딩)
  - BGE-m3 임베딩 + bge-reranker-v2 reranker
  - BM25/vector RRF + 1~2 hop graph traversal
  - Citation 강제 가드레일 — 미달 시 답변 거절
"""
from .rag_agent import answer_with_rag

__all__ = ["answer_with_rag"]
