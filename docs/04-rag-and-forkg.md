# M08 RAG + ForKG-Korea 상세 (★ 학술 contribution #1)

## 학술적 근거

본 시스템의 학술 contribution 1번은 **ForPKG-1.0 framework (Sun & Luo, NEFU 2024.11, arXiv:2411.11090)의 한국 산림 정책 first application**입니다.

ForPKG-1.0은 중국 산림 정책 지식그래프 framework로, 9 entity classes + 11 relation classes 기반의 unsupervised IE 파이프라인을 제안했습니다. 본 연구는 이 framework를 한국 산림 도메인에 처음 적용하여 ForKG-Korea를 구축합니다.

## ontology — 9 entity × 11 relation

`data/ontology/forkg_korea_ontology.yaml` 참고.

### 9 entities
1. **Location** — 행정구역 + 임야 PNU
2. **ForestProduct** — 52 단기임산물 + 가공품
3. **Policy** — 정책·사업·제도 (산림 미래혁신센터·쉼터·스마트팜)
4. **Subsidy** — 보조사업 (~30종, 시군 정착지원 포함)
5. **Organization** — 산림조합 142 + 임업진흥원 + 사업법인 + 정부기관
6. **Person** — 멘토·임업인 (익명화)
7. **Procedure** — 산지전용·임업후계자 등록 등 행정 절차
8. **LegalProvision** — 법령·시행령·시행규칙·별표 청크
9. **DataSource** — 60 공공데이터 카탈로그 자체

### 11 relations
SUITABLE_FOR · GOVERNED_BY · PROVIDES · LOCATED_IN · ELIGIBLE_FOR · SPECIALIZES_IN · REQUIRES · AMENDED_BY · APPLIES_TO · SOURCED_FROM · ADJACENT_TO

### Target scale
- 노드 ≈ 300 (목표 ≥ 250)
- 엣지 ≈ 700 (목표 ≥ 600)

## 추출 파이프라인 (W3-T2)

1. 법제처 OpenAPI로 5법령 + 시행령·시행규칙·별표 → XML
2. lxml 파싱 → 청크 (평균 350자, JSONL)
3. **Claude schema-aligned few-shot** entity·relation 추출 (12 shot 예시)
4. NetworkX MultiDiGraph 적재 → JSON 직렬화 (Neo4j 격하 — 약 300 노드면 in-memory 충분)
5. confidence < 0.7 항목은 human review 큐로

## RAG 검색 흐름

```
사용자 질문
   │
   ├─→ BGE-m3 임베딩 (한국어 SOTA, 1024-dim)
   │      │
   │      └─→ Chroma top-20
   │
   ├─→ BM25 lexical top-20
   │
   ▼
RRF (Reciprocal Rank Fusion, k=60) → top-20 union
   │
   ▼
bge-reranker-v2-m3 reranking → top-5
   │
   ▼
ForKG-Korea 1~2 hop graph traversal (seed = top-5 청크의 LegalProvision 노드)
   │
   ▼
Claude Opus 4.7 + system prompt (citation 강제)
   │
   ▼
CitedAnswer { answer, citations: [≥1], confidence }
   │
   ▼
가드레일: citation 부족 시 → REFUSE response
```

## 가드레일 — citation 강제

답변에 다음 조건이 모두 충족되어야 통과:
1. 청크 ≥ 1개 본문에 인용
2. 인용된 청크의 `law_name` + `article` (또는 `page`)이 답변 텍스트에 명시
3. confidence ≥ 0.6

미달 시 자동 거절:
> "제가 보유한 산림 정책 자료(법제처 OpenAPI 5법령 + 시행지침서)에서 이 질문에 대한 명확한 근거를 찾지 못했습니다. 산림조합중앙회(1544-7170) 또는 산지전용통합정보시스템(1644-0672)으로 문의해 주세요."

## 5 법률 backbone

| # | 법률 | MST | 핵심 활용 |
|---|---|---|---|
| 1 | 산림자원의 조성 및 관리에 관한 법률 | 234571 | M02 산촌 분류 |
| 2 | 임업 및 산촌 진흥촉진에 관한 법률 | 234582 | M06 임업후계자 |
| 3 | **산지관리법** | 234829 | ★ M07 쉼터 7개 룰 |
| 4 | 탄소흡수원 유지 및 증진에 관한 법률 | 234600 | M06 KOC 등록 |
| 5 | 임업·산림 공익직접지불제 운영법 | 239000 | M06 임업직불금 |

## 평가 지표

- **인용 정확도**: ≥ 0.95
- **hallucination rate**: ≤ 3%
- **검증세트 Recall@5**: ≥ 0.85
- **답변 거절율**: 일정 수준 유지 (모르는 질문에 답하지 않음을 보장)
