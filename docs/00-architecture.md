# 시스템 아키텍처 — 7-Layer · 11 모듈 · 5-state Machine

## 7-Layer 개요

```
┌──────────────────────────────────────────────────────────────────────────┐
│ L7 · UI         Next.js 15 · React 19 · Leaflet · VWorld tiles · Recharts │
│                  Zustand · WebSocket streaming                            │
├──────────────────────────────────────────────────────────────────────────┤
│ L6 · API        FastAPI · WebSocket(long-running) · REST · Celery · Redis│
├──────────────────────────────────────────────────────────────────────────┤
│ L5 · LLM Agent  Claude Opus 4.7 + function calling + 5-state machine     │
│                  citation guardrail + hallucination 통제                  │
├──────────────────────────────────────────────────────────────────────────┤
│ L4 · ML Models  LightGBM (M3) · KNN (M4) · PyG GAT (M4 ablation)         │
│                  Prophet+LGBM stacking (M5) · Bootstrap MC calibrated (M5)│
│                  BGE-m3 + bge-reranker-v2 RAG (M6 M8) · SHAP             │
│                  Microclimate downscaling (M10)                          │
├──────────────────────────────────────────────────────────────────────────┤
│ L3 · KG         NetworkX in-memory + JSON · Chroma vector DB              │
├──────────────────────────────────────────────────────────────────────────┤
│ L2 · ETL/Store  PostgreSQL+PostGIS · DuckDB(캐시 grid) · MinIO · Redis     │
├──────────────────────────────────────────────────────────────────────────┤
│ L1 · Ingestion  18+ APIs · 4 web scrapers · Earth Engine · Airflow 6 DAGs│
└──────────────────────────────────────────────────────────────────────────┘
```

## 11 모듈 오케스트레이션 (5-state Machine)

```
User input
   │
   ▼
[State 1 · Profiling]
   M01 (Claude · 3턴 max + hybrid form)
   → UserProfile(27 fields) 확정
   │
   ▼
[State 2 · Candidate Narrowing]  ── 병렬 ──
   M02 (PostGIS · 3축 score)        M11 (5km POI · 4축 score)
   → List[Village] 5~30개 + 4축 레이더
   │
   ▼
[State 3 · Matching]                ── 순차 ──
   M03 (LGBM 28d → Top-5 임산물 + SHAP)
   M04 (KNN primary → Top-K 유사 마을, GAT는 ablation only)
   → Top-3 마을 + Top-5 임산물 카드 제시
   │
   ▼
[State 4 · Decision Package]  ── 사용자 선택 시 ──
   M05 (DuckDB grid lookup) → 5y P10/P50/P90 fan chart
   M06 (룰 + RAG)            → 5y subsidy timeline
   M07 (산지관리법 7 룰)       → 쉼터 적합 + 비용 ±15%
   M09 (시군 1:1)             → 멘토 + 산림조합 + "이번 주 1번 액션"
   │
   ▼
[State 5 · Free Q&A]
   M08 (BM25 + vector RRF + reranker + 1~2 hop traversal)
   → 법령 조항·페이지 강제 인용, 미달 시 거절

[Background]
   M10 (KoMIS 480 + 기상청 + downscaling) → 일일 카카오톡/이메일 push
```

**Latency 목표**: 첫 토큰 ≤ 2초 (M1 첫 응답) · 전체 응답 ≤ 15초 (4 페르소나 14초 시연 실증)

**캐시 전략**:
- M5는 466 × Top-10 × 5 자본 × 4 면적 = **93,000 시나리오 사전 grid → DuckDB → 1초 lookup**
- 외부 API는 Redis 7일 TTL
- 4 페르소나는 hard-coded fixture JSON fallback (`data/fixtures/persona_p0[1-4].json`)

## Function Calling 자동화

Claude는 시스템 프롬프트의 `function_schemas.json` (11개 모듈 JSON schema)을 보고 사용자 자연어 의도가 어느 단계에 진입했는지 판단하여 자동 호출합니다. 사용자는 11 모듈을 **단일 자연어 대화**로만 경험합니다.

핵심 schema 예시 (M03):
```python
def recommend_forest_products(
    profile: UserProfile,
    candidate_villages: List[Village],
    top_k: int = 5,
) -> List[ForestProductRecommendation]: ...
```

전체 함수 시그니처는 `backend/src/agent/function_schemas.json` 참고.

## Storage 매핑

| 데이터 종류 | 저장소 | 이유 |
|---|---|---|
| 공간 SHP (임상도·토양도·산지구분도·466 boundary) | PostgreSQL + PostGIS | GIST 인덱스 + ST_Intersects 공간 join |
| 통계 (임가경제·임산물생산·NFI) | DuckDB | column-oriented · 분석 쿼리 |
| 93k 사전 시나리오 grid | DuckDB | 1초 lookup |
| 법령 RAG 청크 임베딩 | Chroma | 벡터 검색 |
| ForKG-Korea (300 노드 + 700 엣지) | NetworkX in-memory + JSON | 무거운 Neo4j 불필요 |
| KoMIS 1분 raw (~200GB) | MinIO | S3 호환 객체 저장 |
| 외부 API 응답 | Redis (7d TTL) | 발표 당일 API 장애 방어 |
| 모델 아티팩트 (.pkl, .pt) | MinIO (`models/`) | 버전 관리 |

## ETL 6 DAG 주기

| DAG | 주기 | 책임 |
|---|---|---|
| dag1_static_shp | 월 1회 | FGIS SHP 4종 + 466 boundary → PostGIS |
| dag2_statistics | 월 1회 | 산림자원통계 API + KOSIS → DuckDB stats.db |
| dag3_realtime | 시간 단위 | KoMIS + 기상청 + 산불/산사태 + 가격 → Redis |
| dag4_legal | 주 1회 | 법제처 5법령 + 시행지침서 PDF → corpus_legal/ → Chroma |
| dag5_earth_engine | 월 1회 | Sentinel-2 NDVI/EVI + GEDI + PALSAR → ndvi_seasonality.parquet |
| dag6_model_retrain | 월 1회 | LGBM/KNN/GAT/Prophet 재학습 + MC 93k grid 재계산 |

## 시연 안정성 3중 안전장치 (최은영 위원 강조)

1. **사전 계산 grid 캐시** — M5 93,000 시나리오 DuckDB 정적 저장
2. **4 페르소나 hard-coded fallback** — `data/fixtures/persona_p0[1-4].json`
3. **외부 API 7일 TTL Redis 캐시** — 발표 당일 API 장애 무관

추가: 사전 녹화 30초 데모 영상으로 최악 시나리오 대비.
