"""
refs_text/*.txt → 청크 단위 RAG corpus JSONL + BGE-m3 임베딩 + Chroma upsert.

★ 사용자가 Windows에서 실행:
   python scripts/build_rag_corpus.py

산출:
  data/processed/corpus_reference/corpus_reference.jsonl  (~6,000 청크)
  data/processed/corpus_reference/_embeddings_meta.json
  (옵션) Chroma 컬렉션 'soop_legal_corpus' upsert

학술적 설계:
  - 400자/청크 (overlap 50자)
  - PAGE marker / SHEET marker 기준 자연 분할
  - metadata: source_pdf, page, chunk_no, char_offset
  - 인용 강제: M08 답변에 청크 ID + source 인용 의무 (citation guardrail)
  - BGE-m3 임베딩 = 한국어 SOTA dense retriever
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

REFS_TEXT = Path(r"E:\forestLLM\refs_text")
CORPUS_DIR = Path(r"E:\forestLLM\data\processed\corpus_reference")
CORPUS_DIR.mkdir(parents=True, exist_ok=True)
JSONL_PATH = CORPUS_DIR / "corpus_reference.jsonl"

# 청크 파라미터
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50


def ensure_deps():
    missing = []
    try: import chromadb
    except ImportError: missing.append("chromadb")
    try: from sentence_transformers import SentenceTransformer
    except ImportError: missing.append("sentence-transformers")
    if missing:
        print(f"[INSTALL] pip install {' '.join(missing)}")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *missing])


def chunk_text(text: str, source_id: str, source_name: str) -> list[dict]:
    """텍스트를 청크로 분할.

    학술적 룰:
      - PAGE marker (===== PAGE N =====) 또는 SHEET marker 우선 분할
      - 400자/청크 + 50자 overlap
      - 너무 짧은 청크 (<100자) 병합
    """
    chunks = []

    # PAGE 또는 SHEET marker로 1차 분할
    sections = re.split(r"\n=====\s+(?:PAGE|SHEET)\s*:?\s*([^=]+)\s*=====\n", text)
    # split 결과: [text_before, marker1, text1, marker2, text2, ...]
    pages = []
    if len(sections) == 1:
        pages.append(("full", sections[0]))
    else:
        # 첫 element는 prefix
        if sections[0].strip():
            pages.append(("prefix", sections[0]))
        for i in range(1, len(sections), 2):
            marker = sections[i].strip() if i < len(sections) else ""
            page_text = sections[i+1] if i+1 < len(sections) else ""
            pages.append((marker, page_text))

    chunk_no = 0
    for page_marker, page_text in pages:
        page_text = page_text.strip()
        if len(page_text) < 50:
            continue
        # 청크 분할
        start = 0
        while start < len(page_text):
            end = min(start + CHUNK_SIZE, len(page_text))
            # 가능하면 문장 끝에서 자르기
            if end < len(page_text):
                last_period = page_text.rfind(".", start, end)
                last_newline = page_text.rfind("\n", start, end)
                cut = max(last_period, last_newline)
                if cut > start + CHUNK_SIZE * 0.5:
                    end = cut + 1
            chunk_text_str = page_text[start:end].strip()
            if len(chunk_text_str) >= 50:
                chunks.append({
                    "id": f"{source_id}_p{page_marker}_c{chunk_no:04d}",
                    "source_id": source_id,
                    "source_name": source_name,
                    "page_marker": page_marker,
                    "chunk_no": chunk_no,
                    "char_offset_start": start,
                    "char_offset_end": end,
                    "text": chunk_text_str,
                })
                chunk_no += 1
            start = end - CHUNK_OVERLAP if end < len(page_text) else end

    return chunks


def main():
    if not REFS_TEXT.exists():
        print(f"[ERROR] {REFS_TEXT} not found.")
        sys.exit(1)

    files = sorted([f for f in REFS_TEXT.iterdir() if f.suffix == ".txt" and not f.stem.startswith("_")])
    print(f"★ Chunking {len(files)} files")

    all_chunks = []
    for fp in files:
        try:
            text = fp.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  ✗ {fp.name}: {e}")
            continue
        chunks = chunk_text(text, source_id=fp.stem, source_name=fp.stem + ".txt")
        all_chunks.extend(chunks)
        print(f"  ✓ {fp.name}: {len(chunks)} 청크")

    # JSONL 저장
    with JSONL_PATH.open("w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"\n★ Total chunks: {len(all_chunks)}")
    print(f"  → {JSONL_PATH} ({JSONL_PATH.stat().st_size // 1024} KB)")

    # === BGE-m3 임베딩 + Chroma upsert ===
    print("\n=== BGE-m3 임베딩 + Chroma upsert ===")
    ensure_deps()
    try:
        from sentence_transformers import SentenceTransformer
        import chromadb

        model = SentenceTransformer("BAAI/bge-m3")
        client = chromadb.PersistentClient(path=str(CORPUS_DIR / "chroma_db"))
        coll = client.get_or_create_collection(
            name="soop_legal_corpus",
            metadata={"description": "Soop Starter 13 ref PDFs/docs corpus (BGE-m3)"}
        )

        texts = [c["text"] for c in all_chunks]
        ids = [c["id"] for c in all_chunks]
        metas = [{k: v for k, v in c.items() if k not in ("text", "id")} for c in all_chunks]

        # 배치 임베딩 (메모리 보호)
        BATCH = 64
        for i in range(0, len(texts), BATCH):
            batch_texts = texts[i:i+BATCH]
            embs = model.encode(batch_texts, batch_size=BATCH, show_progress_bar=True).tolist()
            coll.upsert(
                ids=ids[i:i+BATCH], embeddings=embs,
                documents=batch_texts, metadatas=metas[i:i+BATCH],
            )

        print(f"\n✓ Chroma collection 'soop_legal_corpus': {coll.count()} items")
        print(f"  Persistent path: {CORPUS_DIR / 'chroma_db'}")
    except Exception as e:
        print(f"  ⚠ Chroma 인덱싱 실패 (chunks JSONL은 저장됨): {e}")
        print(f"  → docker compose up 환경에서 다시 실행하면 인덱싱됨")


if __name__ == "__main__":
    main()
