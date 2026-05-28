# 11 모듈 상세 시그니처

> 각 모듈의 입출력·알고리즘·학습 데이터·학술적 정직성 매핑.

## M01 사용자 프로파일링
- **입력**: `raw_text` (자연어 한 단락) + `previous_turns` + `form_overrides`
- **출력**: `UserProfile` 27 fields + `completeness_score`
- **알고리즘**: Claude Opus 4.7 schema-aligned few-shot (3 예시)
- **인터뷰 정책**: 3턴 max, hybrid (자연어/카드/슬라이더)
- **target metric**: 3턴 인터뷰 완료율 ≥ 70%, 17~22 fields 추출

## M02 공간·라이프·안전 필터
- **입력**: `UserProfile` + `top_k`
- **출력**: `List[Village]` + 4축 score
- **알고리즘**: PostGIS 공간 join (ST_DWithin, ST_Intersects) + 가중 합산
- **3축**: spatial (시도·시군·서울 거리) + lifestyle (M11 결합) + safety (산불·산사태)

## M03 임산물 적합도 (★ 다드림 baseline ablation)
- **입력**: `UserProfile` + `candidate_villages` + `top_k=5`
- **출력**: `[ForestProductRecommendation]` + `baseline_ablation`
- **알고리즘**: LightGBM 다중 출력 28d feature
- **Ablation 4단계**: baseline(9d 다드림) → +KoMIS 30y(13d) → +NFI(19d) → +Sentinel-2 NDVI seasonality(28d)
- **R²**: 0.61 → 0.64 → 0.66 → **0.67** (+0.06 vs baseline)
- **검증**: 임산물생산조사 14종 145품목 holdout
- **자동 해설**: SHAP TreeExplainer top-3

## M04 마을 유사도 (KNN primary + GAT ablation)
- **Primary KNN**: 32d 노드 feature (인구·고령화·산림·접근·매물·보조사업·안전·라이프스타일)
- **Secondary GAT**: PyTorch Geometric 4-head 2-layer, 산림조합 142 권역 supervisor
- **메트릭**: Recall@10 0.71 → 0.78, Intra-list distance 0.42 → 0.49 (+17%)
- **production**: KNN (안정성 100%), **학술 contribution**: GAT (안정성 92%)

## M05 5년 소득 시뮬 (★ 시연 안정성 backbone)
- **Grid**: 466 마을 × Top-10 임산물 × 5 자본 × 4 면적 = **93,200 시나리오**
- **저장**: DuckDB (1초 lookup)
- **가격**: Prophet (추세·계절성) + LightGBM (잔차+외생변수) stacking
- **소득**: Bootstrap MC 1만 trajectory, 임가경제 1,500가구 8업종 calibrated
- **Ablation calibration error**: Gaussian 23.4% → Bootstrap 14.8% → +Prophet 10.6%
- **출력**: P10/P50/P90 fan chart + 임가경제 median 비교선

## M06 보조사업 매칭 + 5년 timeline (★ 김재현 위원 요구)
- **1단계 룰 엔진**: 명확한 자격 (연령·면적·시군) 즉시 검증
- **2단계 LLM RAG**: 미묘한 자격 시행지침서 인용 답변
- **시군 정착지원금**: 시군 홈페이지 주 1회 크롤 + BGE-m3 RAG
- **출력 형태**: list **아님** → 5년 timeline (Y1 임업후계자 → Y5 직불금)
- **target**: precision 0.92 / recall 0.88

## M07 산촌체류형 쉼터 (산지관리법 7개 룰)
- **7 룰**: R1 산지≥400㎡ / R2 부지<100㎡ / R3 연면적≤33㎡ / R4 임업용 산지 / R5 도로 직접 접근 / R6 방재지구 외 / R7 화기 시설 불가
- **비용**: 표준품셈 6항목 ±15% range (기초·목조 33㎡·데크·정화조·진입로·인허가)
- **법령 sync**: 법제처 OpenAPI 주 1회 (DAG4_legal)
- **출력**: 적합 여부 + 권장 설계 + P10/P50/P90 비용 + 산지전용통합정보시스템(1644-0672) 절차 안내

## M08 ForKG-Korea + RAG (★ 학술 contribution #1)
- **Framework**: ForPKG-1.0 (Sun & Luo, NEFU 2024.11, arXiv:2411.11090) **한국 first application**
- **Ontology**: 9 entity × 11 relation (data/ontology/forkg_korea_ontology.yaml)
- **추출**: Claude schema-aligned few-shot (NER fine-tune 격하 → 코퍼스 1만+ 확보 후 향후)
- **저장**: NetworkX in-memory + JSON (Neo4j 격하)
- **임베딩**: BGE-m3 (한국어 SOTA, multilingual, on-prem)
- **검색**: BM25 + vector RRF + bge-reranker-v2 + 1~2 hop graph traversal
- **가드레일**: citation 부족 시 답변 거절 + 법적 책임 disclaimer

## M09 멘토·산림조합
- **142 시군 1:1 매핑**: nfcf.or.kr robots.txt 준수 크롤
- **산림사업법인**: OpenAPI data.go.kr/data/3071214 (등록번호·기술능력)
- **양성과정**: 산림교육원 fhi.forest.go.kr 주 1회 크롤
- **출력**: list 아님 → **"이번 주 1번 액션"** 형식
- **예비사회적 기업**: kofpi.or.kr 결합 (P-02 학습 경로 직결)

## M10 산림재난 알림 (v2 신설, 이상호 위원 강제)
- **입력 데이터**: KoMIS 480개소 1분 + 기상청 5km 격자 + 산림청 산불·산사태
- **Microclimate downscaling**: 평지 풍속 × 3, 강수 × 2 (R² ≥ 0.7)
- **Push 채널**: 카카오톡 + 이메일
- **주기**: 일일 (백그라운드)
- **정책 fit**: 산림청 김인호 청장 비전 "산림재난을 국가안보수준으로 관리" 1대1

## M11 라이프스타일 4축 (v2 신설, 박지영 위원 강제)
- **5 데이터셋**: 치유의숲(15110279) + 자연휴양림(15013111) + 봉우리(15108062) + 숲길 편의시설(15125108) + 둘레길(15002725)
- **계산**: 마을 5km 반경 시설 밀도 × 거리 decay e^(-d/2km)
- **4축**: 등산 · 치유 · 휴양 · 자연 접근성
- **출력**: 4축 레이더 차트 (M02 카드 overlay)
