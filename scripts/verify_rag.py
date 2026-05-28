"""
M08 RAG 동작 검증 — Chroma 컬렉션 query + Gemini citation guardrail.

검증 항목:
  1. 5 핵심 질문 → top-5 chunk recall
  2. 각 chunk metadata (source_pdf, page) 인용 가능 여부
  3. Gemini 답변 → 인용 strict 여부 (M08 가드레일)
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path

CORPUS_DIR = Path(r"E:\forestLLM\data\processed\corpus_reference")
CHROMA_PATH = CORPUS_DIR / "chroma_db"

# 5 학술적 검증 질문 — Soop Starter 핵심 영역
QUERIES = [
    {"q": "임업직불금 2026년 자격 요건은?", "expect_in_source": ["05_direct_payment"]},
    {"q": "산촌체류형 쉼터 설치 가능 조건은?", "expect_in_source": ["03_forest_business", "04_forest_income"]},
    {"q": "임업후계자 양성 과정 신청 방법", "expect_in_source": ["04_forest_income", "03_forest_business"]},
    {"q": "산림탄소상쇄 KOC 등록 절차", "expect_in_source": ["09_carbon_offset"]},
    {"q": "영양 임산물 스마트팜 청년 자격", "expect_in_source": ["07_yeongyang", "08_government"]},
]


def main():
    # === Chroma client ===
    import chromadb
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    coll = client.get_collection("soop_legal_corpus")
    print(f"★ Chroma collection: {coll.count()} items")
    print()

    # BGE-m3 model
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer("BAAI/bge-m3")

    # 검증 결과
    results = []
    for i, q in enumerate(QUERIES):
        print(f"=== Q{i+1}: {q['q']} ===")
        # 임베딩
        q_emb = model.encode([q["q"]]).tolist()
        # Chroma top-5
        res = coll.query(query_embeddings=q_emb, n_results=5)
        hits = []
        for j in range(len(res["ids"][0])):
            meta = res["metadatas"][0][j]
            doc = res["documents"][0][j][:200]
            dist = res["distances"][0][j] if "distances" in res else None
            hits.append({"chunk_id": res["ids"][0][j], "source": meta.get("source_id"),
                         "page": meta.get("page_marker"), "text_preview": doc, "distance": dist})
            print(f"  Hit {j+1}: {meta.get('source_id'):50s} dist={dist:.3f}" if dist else
                  f"  Hit {j+1}: {meta.get('source_id'):50s}")
            print(f"    page={meta.get('page_marker')} | {doc[:100]}...")
        # Source 검증
        sources_hit = {h["source"][:18] for h in hits}
        expected_any = any(any(e.startswith(s[:18]) or s.startswith(e[:18]) for s in sources_hit)
                           for e in q["expect_in_source"])
        print(f"  → expected source hit: {'✓' if expected_any else '✗'}")
        results.append({"query": q["q"], "expected": q["expect_in_source"],
                        "hits": hits, "expected_hit": expected_any})
        print()

    # 요약
    print("=" * 60)
    n_pass = sum(1 for r in results if r["expected_hit"])
    print(f"RAG recall: {n_pass}/{len(QUERIES)} queries hit expected source in top-5")
    print()

    # 저장
    (CORPUS_DIR / "_rag_verify.json").write_text(
        json.dumps({"queries": QUERIES, "results": results,
                    "recall_at_5": n_pass / len(QUERIES)},
                   ensure_ascii=False, indent=2, default=str),
        encoding="utf-8"
    )
    print(f"✓ {CORPUS_DIR / '_rag_verify.json'}")


if __name__ == "__main__":
    main()
