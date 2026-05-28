"""
DAG4 — Legal 법령 RAG corpus (주 1회)
=====================================
법제처 OpenAPI 5법령 + 시행령·시행규칙·별표 + 시행지침서 PDF + 시군 조례
→ 청크(평균 350자) → Chroma 벡터 DB (BGE-m3 임베딩).

5 핵심 법률:
  1. 산림자원의 조성 및 관리에 관한 법률
  2. 임업 및 산촌 진흥촉진에 관한 법률
  3. 산지관리법 (★ M07 쉼터 7개 룰)
  4. 탄소흡수원 유지 및 증진에 관한 법률 (★ KOC)
  5. 임업·산림 공익직접지불제도 운영에 관한 법률 (★ 임업직불금)

W1-T5 산출물.
"""
from __future__ import annotations
import json, os, re
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator

DEFAULT_ARGS = {"owner": "soop", "retries": 3, "retry_delay": timedelta(minutes=10)}

LAW_DIR = Path("/opt/airflow/data/raw/legal")
CORPUS_DIR = Path("/opt/airflow/data/processed/corpus_legal")

LAWS = [
    {"name": "산림자원법",           "mst": "234571"},
    {"name": "임업산촌진흥촉진법",   "mst": "234582"},
    {"name": "산지관리법",           "mst": "234829"},  # ★ M07
    {"name": "탄소흡수원유지증진법", "mst": "234600"},  # ★ KOC
    {"name": "임업산림공익직불제법", "mst": "239000"},  # ★ 임업직불금
]


def fetch_law_xml(law_name: str, mst: str, **ctx):
    import httpx
    oc = os.environ.get("LAW_GO_KR_OC", "zxsa0716@kookmin.ac.kr")
    LAW_DIR.mkdir(parents=True, exist_ok=True)
    for target in ["law", "lawjosub", "licbyl"]:
        out = LAW_DIR / f"{law_name}_{target}.xml"
        url = f"http://www.law.go.kr/DRF/lawService.do?OC={oc}&target={target}&MST={mst}&type=XML"
        r = httpx.get(url, timeout=30)
        out.write_bytes(r.content)
    return f"{law_name}: 3 XML fetched"


def chunk_to_jsonl(**ctx):
    """XML → 청크 단위 JSONL (평균 350자) → corpus_legal/."""
    from lxml import etree
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = CORPUS_DIR / "legal_chunks.jsonl"
    chunks = []
    for xml in LAW_DIR.glob("*.xml"):
        try:
            tree = etree.parse(str(xml))
        except Exception as e:
            ctx["ti"].log.warning(f"parse fail {xml}: {e}")
            continue
        law_name = xml.stem.split("_")[0]
        for jo in tree.iter():
            text = "".join(jo.itertext()).strip()
            if 200 <= len(text) <= 500:
                chunks.append({
                    "id": f"{xml.stem}__{jo.tag}__{len(chunks)}",
                    "law_name": law_name,
                    "article": jo.get("조문번호") or jo.tag,
                    "text": re.sub(r"\s+", " ", text)[:500],
                    "source_url": f"https://www.law.go.kr/법령/{law_name}",
                })
    with out_path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    ctx["ti"].log.info(f"chunks: {len(chunks)} → {out_path}")
    return len(chunks)


def index_to_chroma(**ctx):
    """BGE-m3 임베딩 → Chroma."""
    import chromadb
    from sentence_transformers import SentenceTransformer
    encoder = SentenceTransformer("BAAI/bge-m3", device="cpu")
    client = chromadb.HttpClient(host=os.getenv("CHROMA_HOST", "chroma"), port=int(os.getenv("CHROMA_PORT", "8000")))
    col = client.get_or_create_collection("soop_legal_corpus")
    src = CORPUS_DIR / "legal_chunks.jsonl"
    chunks = [json.loads(line) for line in src.open(encoding="utf-8")]
    if not chunks:
        return 0
    texts = [c["text"] for c in chunks]
    embeddings = encoder.encode(texts, show_progress_bar=True, normalize_embeddings=True).tolist()
    col.upsert(ids=[c["id"] for c in chunks], documents=texts,
               metadatas=[{"law_name": c["law_name"], "article": c["article"], "source_url": c["source_url"]} for c in chunks],
               embeddings=embeddings)
    return f"Chroma upserted: {len(chunks)}"


with DAG(
    dag_id="dag4_legal",
    default_args=DEFAULT_ARGS,
    description="법제처 5법령 → 청크 → BGE-m3 → Chroma (M08 RAG corpus)",
    schedule="@weekly", start_date=datetime(2026, 5, 12), catchup=False,
    tags=["W1-T5", "legal", "rag"],
) as dag:
    fetch_tasks = [
        PythonOperator(task_id=f"fetch_{law['name']}",
                       python_callable=fetch_law_xml,
                       op_kwargs={"law_name": law["name"], "mst": law["mst"]})
        for law in LAWS
    ]
    chunk = PythonOperator(task_id="chunk_to_jsonl", python_callable=chunk_to_jsonl)
    index = PythonOperator(task_id="index_to_chroma", python_callable=index_to_chroma)
    fetch_tasks >> chunk >> index
