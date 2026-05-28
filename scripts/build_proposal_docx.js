// Soop Starter — 본 대회 제출용 기획서 PDF 30p (.docx)
// 사용: node scripts/build_proposal_docx.js
//
// 필요: npm install -g docx
// 출력: data/processed/deliverables/soop_starter_proposal.docx

const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, PageOrientation, LevelFormat,
  TabStopType, TabStopPosition, TableOfContents, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
  ExternalHyperlink, Bookmark, InternalHyperlink, FootnoteReferenceRun
} = require('docx');

// ============================================================================
// Constants
// ============================================================================
const PAGE_W = 12240;  // US Letter
const PAGE_H = 15840;
const MARGIN = 1440;
const CONTENT_W = PAGE_W - MARGIN * 2;  // 9360

const FOREST_DEEP = "1F3320";
const FOREST = "2D4A2B";
const OCHRE = "B8893E";
const BARK = "3F2A1D";
const PAPER_DEEP = "EBE3D2";
const RULE = "C9BCA3";

const border = (color = RULE, size = 1) => ({ style: BorderStyle.SINGLE, size, color });
const borders = (color = RULE) => ({
  top: border(color), bottom: border(color),
  left: border(color), right: border(color),
});

// ============================================================================
// Helpers
// ============================================================================
function H1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 240 },
    children: [new TextRun({ text, bold: true, size: 32, font: "Noto Serif KR" })],
  });
}
function H2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 240, after: 120 },
    children: [new TextRun({ text, bold: true, size: 26, font: "Pretendard" })],
  });
}
function H3(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 180, after: 80 },
    children: [new TextRun({ text, bold: true, size: 22, color: FOREST_DEEP, font: "Pretendard" })],
  });
}
function P(text, opts = {}) {
  return new Paragraph({
    spacing: { after: 120, line: 360 },
    alignment: opts.align || AlignmentType.JUSTIFIED,
    children: [new TextRun({ text, size: opts.size || 22, font: "Pretendard", ...opts })],
  });
}
function Bullet(text, level = 0) {
  return new Paragraph({
    numbering: { reference: "bullets", level },
    spacing: { after: 60 },
    children: [new TextRun({ text, size: 22, font: "Pretendard" })],
  });
}
function PageBr() {
  return new Paragraph({ children: [new PageBreak()] });
}

function cell(text, opts = {}) {
  return new TableCell({
    borders: borders(opts.borderColor || RULE),
    width: { size: opts.width, type: WidthType.DXA },
    shading: opts.shading
      ? { fill: opts.shading, type: ShadingType.CLEAR }
      : undefined,
    margins: { top: 80, bottom: 80, left: 120, right: 120 },
    children: [
      new Paragraph({
        alignment: opts.align || AlignmentType.LEFT,
        children: [new TextRun({
          text: String(text), size: opts.size || 20,
          bold: opts.bold, color: opts.color, font: "Pretendard",
        })],
      }),
    ],
  });
}

function table(headers, rows, columnWidths) {
  return new Table({
    width: { size: columnWidths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths,
    rows: [
      new TableRow({
        tableHeader: true,
        children: headers.map((h, i) =>
          cell(h, { width: columnWidths[i], bold: true, color: "FFFFFF",
                    shading: FOREST_DEEP, align: AlignmentType.CENTER })),
      }),
      ...rows.map((row) =>
        new TableRow({
          children: row.map((c, i) => cell(c, { width: columnWidths[i] })),
        })),
    ],
  });
}

// ============================================================================
// Cover Page
// ============================================================================
const cover = [
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 2400, after: 240 },
    children: [new TextRun({ text: "2026 산림 공공데이터·AI 활용 창업경진대회",
                              bold: true, size: 22, color: FOREST_DEEP, font: "Pretendard" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60 },
    children: [new TextRun({ text: "제품·서비스 개발 트랙",
                              size: 18, color: BARK, font: "Pretendard" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 600, after: 240 },
    children: [new TextRun({ text: "숲스타터",
                              bold: true, size: 80, color: FOREST_DEEP, font: "Noto Serif KR" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 600 },
    children: [new TextRun({ text: "Soop Starter",
                              size: 36, italics: true, color: BARK, font: "Noto Serif KR" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60 },
    children: [new TextRun({ text: "한국 산촌 청년 임업인 진입 의사결정 지원 시스템",
                              size: 28, bold: true, color: BARK, font: "Pretendard" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 1200 },
    children: [new TextRun({ text: "공간–시계열–지식그래프 융합 다중모달 추천 시스템",
                              size: 22, italics: true, color: BARK, font: "Pretendard" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60 },
    children: [new TextRun({ text: "출품자 · Heedo (국민대학교)",
                              size: 22, font: "Pretendard" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60 },
    children: [new TextRun({ text: "제출 마감 2026.06.19 18:00",
                              size: 20, color: BARK, font: "Pretendard" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 60 },
    children: [new TextRun({ text: "본선 발표 2026.07.21~22",
                              size: 20, color: BARK, font: "Pretendard" })],
  }),
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 600 },
    children: [new TextRun({ text: "TR-2026-001 · Technical Research Report",
                              size: 16, italics: true, color: BARK, font: "JetBrains Mono" })],
  }),
  PageBr(),
];

// ============================================================================
// Abstract
// ============================================================================
const abstract = [
  H1("초록 (Abstract)"),
  P("본 연구는 한국 산림 부문에서 가장 오래되고 가장 풀리지 않은 세 가지 구조적 모순 — 사유림 67% 영세 구조, 산촌 466 읍면 인구소멸 임계점, 그리고 2026년 신규 정책 3개의 동시 도입(산림 미래혁신센터 90억, 산촌체류형 쉼터, 영양 임산물 스마트팜 105억) — 을 단일 디지털 의사결정 도구로 해소할 것을 목표로 한다. 본 시스템 숲스타터(Soop Starter)는 도시 청년이 자연어 인터뷰 한 번을 통해 적합 산촌 마을, 적합 임산물 5종, 산촌체류형 쉼터 입지·비용, 5년 임가 소득 시나리오, 청년임업인 보조사업 자동 매칭, 인근 산림조합·멘토를 통합 결정 패키지로 받는 LLM 에이전트 기반 다중모달 추천 시스템이다."),
  P("방법론적으로는 ForPKG-1.0 framework (Sun & Luo, arXiv:2411.11090) 의 한국 산림 정책 first application으로서 ForKG-Korea (669 노드 · 962 엣지) 를 구축하고, 466 산촌 × 52 임산물 적합도 매트릭스와 임가경제조사 1,500가구 8업종 분포로 calibrate 된 Monte Carlo 5년 소득 baseline 을 한국 최초로 제시한다. 데이터 측면에서는 산림청·한국임업진흥원·한국산림복지진흥원·한국등산·트레킹지원센터 4개 주관기관 약 25개 데이터셋 + D:\\craft 17 source (DEM 5m, MKPRISM 78GB, 임상도 12GB 등) + 7,992 RAG corpus 청크를 단일 multi-modal 파이프라인으로 통합한 첫 시스템이다."),
  P("기술 측면에서는 LightGBM 적합도 매칭, KNN baseline + PyTorch Geometric GAT contrastive ablation, Prophet–LightGBM stacking 가격 예측, Bootstrap Monte Carlo 93,200 시나리오 사전 계산 grid (1초 lookup), BGE-m3 + bge-reranker-v2 + 1~2 hop graph traversal RAG, Gemini 2.5-flash 함수 호출 11 모듈 오케스트레이션을 결합한다. M08 인용 강제 가드레일 (citation 미달 시 답변 거절) 로 hallucination 통제."),
  new Paragraph({
    spacing: { before: 360, after: 120 },
    children: [
      new TextRun({ text: "Keywords: ", bold: true, size: 20, color: FOREST_DEEP, font: "JetBrains Mono" }),
      new TextRun({ text: "Decision Support System · Knowledge Graph · LLM Agent · Spatial Recommender · Korean Forestry · Rural Transition · Multi-modal Fusion · Public Data Integration",
                    size: 20, font: "JetBrains Mono" }),
    ],
  }),
  PageBr(),
];

// ============================================================================
// 목차
// ============================================================================
const toc = [
  H1("목차 / Table of Contents"),
  new TableOfContents("Soop Starter Proposal", { hyperlink: true, headingStyleRange: "1-2" }),
  PageBr(),
];

// ============================================================================
// 1. 문제 정의 — 3가지 구조적 모순
// ============================================================================
const sec1 = [
  H1("1. 문제 정의 — 한국 산림 부문 3가지 구조적 모순"),
  H2("1.1 사유림 67% 영세 구조"),
  P("한국 전체 산림 면적의 67%를 차지하는 사유림은 산주의 평균 보유 면적이 1ha 미만이며, 그중 다수가 도시 거주 부재산주이거나 경영 의사 자체를 포기한 영세 구조에 머물러 있다. 산림경영학은 산주가 이미 임야를 보유했다는 가정 위에서 Faustmann–Hartman 회전기 결정 등 운영 결정을 다루어 왔으나, 산주가 아직 산주가 아닌 진입 단계 사용자를 위한 의사결정 도구는 존재하지 않는다."),
  H2("1.2 466 산촌 읍면 인구소멸 임계점"),
  P("산림기본법 시행령 §3에 따라 분류되는 466개 산촌 읍면 (2024년 산촌기초조사 기준, refs/02_sanchon_466_2024.pdf 정확 추출 467 BJCD ✓) 이 인구 소멸 임계점에 도달했으며, 평균 고령화율이 전국 읍면 평균을 크게 상회한다. 임업 후계자가 부재한 마을이 빠르게 늘고 있다."),
  H2("1.3 2026 신규 정책 3개 동시 도입 + 정보 비대칭"),
  P("산림청은 2026년에 산림 미래혁신센터 90억 원 신설, 산촌체류형 쉼터 제도 도입, 영양 임산물 스마트팜 실증단지 105억 원 (2026~2028) 등 신규 정책 3개를 동시에 도입했다. 그러나 도시에 거주하는 청년 잠재 임업인이 이 정책들을 종합적으로 이해하고 자신의 자본·기술·라이프스타일에 맞춰 결정할 수 있는 단일 디지털 진입 도구가 존재하지 않는다."),
  H3("핵심 통찰"),
  P("본 연구는 이 셋을 하나의 결정 문제로 재정의한다. 즉 도시 청년이 도시를 떠나 산촌에 진입하면서 임업이라는 새로운 산업으로 동시에 전환하는 결정은 단일 변수 최적화가 아니라 공간(어느 마을), 시계열(언제, 5년에 걸쳐 어떻게), 정책(어떤 보조사업), 사회(어떤 멘토·조합), 라이프스타일(가족·근무·자연) 다섯 축을 동시에 고려해야 하는 다중 결정 문제로 정의된다. 이를 가장 강력하게 풀 수 있는 패러다임이 자연어 인터뷰 가능한 LLM 에이전트이다."),
  PageBr(),
];

// ============================================================================
// 2. 학술 contribution 3종
// ============================================================================
const sec2 = [
  H1("2. 학술 Contribution 3종"),
  H2("2.1 Methodological — ForKG-Korea (Korea-first ForPKG-1.0 application)"),
  P("ForPKG-1.0 (Sun & Luo, NEFU 2024.11, arXiv:2411.11090) 프레임워크의 한국 산림 정책 first application. 9 entity 클래스 (Location · ForestProduct · Policy · Subsidy · Organization · Person · Procedure · LegalProvision · DataSource) × 11 relation (SUITABLE_FOR · GOVERNED_BY · PROVIDES · LOCATED_IN · ELIGIBLE_FOR · SPECIALIZES_IN · REQUIRES · AMENDED_BY · APPLIES_TO · SOURCED_FROM · ADJACENT_TO) 으로 한국 산림 정책 지식그래프 backbone 을 구축한다."),
  P("구축 실적: 669 노드 + 962 엣지 (W3-T2 목표 250/600 대비 +268% / +160%). 노드 분포: Location 589 (시도 13 + 시군 119 + 466 산촌) · Subsidy 32 · DataSource 19 · ForestProduct 10 · LegalProvision 8 · Organization 4 · Procedure 4 · Policy 3. 저장: NetworkX in-memory + JSON 직렬화 (Neo4j 격하)."),
  H2("2.2 Empirical — 466×52 적합도 매트릭스 + 5년 Monte Carlo Baseline"),
  P("한국 최초의 466 산촌 읍면 × 52 단기임산물 적합도 매트릭스 + 임가경제조사 1,500임가 8업종 calibrated Monte Carlo 5년 소득 baseline. 이는 산림 정책 효과 분석과 임가 소득 안정화 연구의 정량 baseline으로 후속 연구가 재사용 가능하다."),
  P("LightGBM 28차원 feature: 토양(우점·pH·유기물·토심) + 산악기상 30년 평균(기온·강수·일조·서리일수) + DEM 5m(표고·경사·방위) + 임상(산림 피복률·임령·우점 수종) + Sentinel-2 NDVI 30년 seasonality + 사용자 매칭. 5-fold CV R² = 0.356 ± 0.009 (synth, W3 실데이터 swap 후 0.67 목표). 다드림 baseline(R² 0.61) 대비 ablation 비교."),
  P("Monte Carlo: Prophet(추세·계절성) + LightGBM(잔차+외생변수) stacking + Bootstrap MC 임가경제 1,500가구 calibrate. 466 × Top-10 × 5 자본 × 4 면적 = 93,200 시나리오 사전 grid → DuckDB 1초 lookup. 임가경제 median calibration error 23.4% → 10.6% 절반 이하 개선."),
  H2("2.3 Applied — 4 주관기관 First Integration"),
  P("한국 산림청 + 한국임업진흥원 + 한국산림복지진흥원 + 한국등산·트레킹지원센터 4개 주관기관 약 25개 데이터셋을 단일 multi-modal 추천 파이프라인으로 통합한 첫 시스템. 88팀 중 우리만 가능한 차별화로, 산림청 산림자원통계 OpenAPI (selectStatList1, refs/10 확정) + 한국임업진흥원 다드림 (BYOA 패턴) + 산림복지진흥원 치유의숲 5개 데이터셋 + 등산트레킹지원센터 봉우리·둘레길 POI 를 모두 활용한다."),
  PageBr(),
];

// ============================================================================
// 3. 11 모듈 architecture
// ============================================================================
const sec3 = [
  H1("3. 11 모듈 Architecture"),
  H2("3.1 7-Layer Stack"),
  P("L7 UI: Next.js 15 + Leaflet + VWorld tiles + Recharts + WebSocket streaming"),
  P("L6 API: FastAPI + WebSocket (long-running) + Celery + Redis"),
  P("L5 LLM Agent: Gemini 2.5-flash + function calling + 5-state machine + 11 모듈 오케스트레이션"),
  P("L4 ML Models: LightGBM (M3) · KNN (M4) · PyG GAT (M4 ablation) · Prophet+LGBM stacking (M5) · Bootstrap MC calibrated (M5) · BGE-m3 + bge-reranker-v2 RAG (M6 M8) · SHAP · Microclimate downscaling (M10)"),
  P("L3 KG: NetworkX in-memory + JSON · Chroma vector DB (7,992 청크)"),
  P("L2 ETL/Store: PostgreSQL + PostGIS · DuckDB · MinIO · Redis (7d TTL)"),
  P("L1 Ingestion: 18+ APIs · 4 web scrapers · Google Earth Engine · Airflow 6 DAGs"),
  H2("3.2 11 모듈 요약표"),
  table(
    ["ID", "모듈", "알고리즘", "출력"],
    [
      ["M01", "사용자 프로파일링", "Gemini + Pydantic 27d, 3턴 max", "UserProfile 27 fields"],
      ["M02", "공간·라이프·안전 필터", "PostGIS join, 3축 score", "5~30 후보 마을"],
      ["M03", "임산물 적합도", "LightGBM 28d × 52 품목 + SHAP", "Top-5 + 자동 해설"],
      ["M04", "마을 유사도", "KNN (prod) + GAT contrastive (abl)", "Top-K + 다양성"],
      ["M05", "5년 소득 시뮬", "Prophet+LGBM + Bootstrap MC", "P10/P50/P90 fan chart"],
      ["M06", "보조사업 매칭", "32 룰 + RAG verify", "5년 timeline"],
      ["M07", "쉼터 입지 평가", "산지관리법 7 룰 + 표준품셈 6", "비용 ±15%"],
      ["M08", "ForKG-Korea + RAG", "BGE-m3 + RRF + traversal + 인용 강제", "Cited Answer"],
      ["M09", "멘토·산림조합", "142 시군 1:1 + 기술능력 매칭", "이번 주 1번 액션"],
      ["M10", "산림재난 알림", "Microclimate downscaling + push", "일일 알림"],
      ["M11", "라이프스타일 score", "5km 시설 밀도 + 거리 decay", "4축 (등산·치유·휴양·자연)"],
    ],
    [600, 2000, 3500, 3260]
  ),
  P("Latency 목표: 첫 토큰 ≤ 2초, 전체 응답 ≤ 15초 (4 페르소나 14초 시연 실증)"),
  PageBr(),
];

// ============================================================================
// 4. 4 페르소나 시연
// ============================================================================
const sec4 = [
  H1("4. 4 페르소나 시연"),
  P("본 시스템의 4 페르소나 (P-01~P-04) 는 산림기본법 §3 공식 466 산촌 중에서 정확히 매칭된 거점과 행정구역코드, KMA 격자 (nx, ny), 위경도, 측정 elevation/slope, 실시간 토지 거래가까지 모두 검증된 시연 backbone 이다."),
  table(
    ["#", "거점 (BJCD)", "격자 (nx,ny)", "측정 elev", "평균 토지가", "Hit 2026 신규"],
    [
      ["P-01 김도현 35 IT", "평창 진부면 5176036000", "(87, 129)", "838 m", "5,560만/1,069㎡", "산촌체류형 쉼터"],
      ["P-02 이수진 28 디자이너", "충주 수안보면 4313032500", "(78, 111)", "300 m", "9,412만/736㎡", "임업후계자 + 인턴십"],
      ["P-03 박재훈 45 회사원", "진안 부귀면 5272038000", "(67, 89)", "456 m", "3,165만/6,022㎡", "산림 미래혁신센터 90억 + KOC"],
      ["P-04 정민호 30 IT", "영양 일월면 4776033000", "(98, 109)", "487 m", "2,606만/2,587㎡", "★ 영양 스마트팜 105억"],
    ],
    [2200, 2600, 1200, 800, 1300, 1260]
  ),
  H2("4.1 P-04 정민호 시연 흐름 (2026 신규 정책 직결, 14초)"),
  P("입력: \"30세 IT 풀스택 개발자, 자본 3천만, 영양 어수리 임산물 스마트팜 임대형 진입 희망\". M01 (1초) UserProfile 27 fields 확정 → M02 (3초) 영양 일월면 매칭 → M03 (5초) 어수리 적합도 0.94 + SHAP (시설재배 5배 수확량) → M05 (7초) 5년 P50 +2.7억 → M07 (8초) 스마트팜 임대형 → 쉼터 불가, 단지 숙소 안내 → M06 (10초) 영양 105억 사업 ✓ 18~40세 청년 자격 + 영양군 청년 귀산촌 1,000만 + 임업후계자 → M09 (12초) 영양산림조합 + 어수리 종묘 leads → 통합 \"이번 주 1번 액션: 영양 임산물 스마트팜 공모 신청 일정 확인\""),
  PageBr(),
];

// ============================================================================
// 5. 데이터 인벤토리
// ============================================================================
const sec5 = [
  H1("5. 데이터 인벤토리 — 5 API + D:\\craft 17 source + 7,992 청크"),
  H2("5.1 5 검증 API (live test 2026-05-26)"),
  table(
    ["API", "Endpoint", "검증", "활용 모듈"],
    [
      ["Gemini 2.5-flash", "generativelanguage.googleapis.com", "✓ 한국어 정확", "M01 M06 M08 (모든 LLM 호출)"],
      ["토지 실거래가", "1613000/RTMSDataSvcLandTrade", "✓ 240 거래/4 페르소나", "M07"],
      ["기상청 단기예보", "1360000/VilageFcstInfoService_2.0", "✓ 5km 격자 정확", "M10"],
      ["기상청 산악예보", "apihub.kma.go.kr/api/typ08", "✓ 산악 5건/거점", "M10 (KoMIS 역할)"],
      ["산림사업법인", "api.forest.go.kr/openapi/...", "✓ 시군명 검색", "M09"],
      ["산림자원통계", "1400000/frsas1/selectStatList1", "✓ refs/10 확정", "M03 M05 (DAG2)"],
    ],
    [2200, 3000, 2200, 1960]
  ),
  H2("5.2 D:\\craft\\CRAFT\\data — 17 source read-only adapter"),
  Bullet("임상도 imsangdo2024.gpkg (12 GB) — M03 수종·임령 feature"),
  Bullet("입지토양도 soil.gpkg (22 GB) — M03 pH·유기물·토심"),
  Bullet("DEM_5m (373 GB) — 6 layer: dem·slope·aspect_cos/sin·TWI·curvatu"),
  Bullet("MKPRISM (78 GB) — KoMIS 대체 일별 격자 기상 RHM 2000년~"),
  Bullet("NFI 5/6/7 (xlsx, 323 MB) — 16만 표본점 enriched feature"),
  Bullet("행정경계 (440 MB) — 5,007 읍면동 SHP, 466 산촌 boundary backbone"),
  Bullet("산불이력 FR03to20 (2003-2020, 8,115 events) — M02 안전 + M10"),
  Bullet("산사태포인트 LS_2011-2014 (1,354 pts) — M02 안전 + M10"),
  Bullet("등산로 dungsanro.gpkg + trail.gpkg (123 MB, 59,403 features) — M11"),
  Bullet("도로중심선_merged (5.3 GB) — M07 도로 직접 접근 룰"),
  Bullet("임도망도 (28 MB) — 임업 접근성 feature"),
  Bullet("SSP2/SSP5 (42 GB) — 향후 기후 시나리오"),
  H2("5.3 RAG corpus 13 PDF/docx/xlsx/hwp → 7,992 청크"),
  Bullet("01 임산물생산조사 2024 (651K 자, 2,258 청크)"),
  Bullet("02 산촌기초조사 466 (467 BJCD 정확 추출 매칭)"),
  Bullet("03 산림사업종합자금 + 04 산림소득분야 + 05 임업·산림 공익직접지불 (3,966 청크)"),
  Bullet("06 산악예보 API + 11 KMA 단기예보 + 12 격자 lookup (1,523 청크)"),
  Bullet("07 영양 스마트팜 + 08 정부혁신 + 09 KOC + 10 산림자원통계 + 13 토지실거래 (250 청크)"),
  Bullet("저장: data/processed/corpus_reference/chroma_db (Chroma persistent, BGE-m3)"),
  PageBr(),
];

// ============================================================================
// 6. 위험·평가
// ============================================================================
const sec6 = [
  H1("6. 위험·평가 매트릭스"),
  H2("6.1 식별된 6 위험과 우회"),
  table(
    ["위험", "우회 전략"],
    [
      ["산림조합 142개 위치 OpenAPI 부재", "nfcf.or.kr robots.txt 준수 일별 크롤. 시군 단위 1:1 매핑. 협업 공문 불사용."],
      ["임야 매물 산주 신원 비공개", "다드림 BYOA 패턴 (사용자 본인 인증) + 산림조합 임야거래장터 공개 매물만 활용"],
      ["농림위성 CAS500-4 안정화 시점 발표일 겹침", "MVP 제외 → Sentinel-2 + GEDI + PALSAR-2 + MKPRISM 78GB 로 충분. 향후 로드맵."],
      ["산촌체류형 쉼터 시행령 시행 시점 불확실", "입법예고 종료 후 시행 임박. 정책 도입 자체가 framing power. 시행 전이라도 가치 명분 강화."],
      ["KOC 거래단가 비공개", "KAU 단가 약 80% 추정 + 학술 case study + 산림탄소센터 042-603-7315 상담 안내"],
      ["LLM hallucination on 정책 답변", "M08 RAG 인용 강제 + citation 미달 시 답변 거절 + 법적 책임 disclaimer"],
    ],
    [2800, 6560]
  ),
  H2("6.2 평가 기준 4축 매트릭스"),
  table(
    ["평가 기준", "본 연구 답변"],
    [
      ["① 산림 공공데이터 활용도",
       "4개 주관기관 약 25개 데이터셋 + D:\\craft 17 source + 7,992 RAG 청크 + 5 API live (88팀 중 모두 활용 첫 작품)"],
      ["② 독창성",
       "ForPKG-1.0 한국 first application (669 노드 + 962 엣지) + 466×52 적합도 매트릭스 + 5년 Monte Carlo baseline + 32 보조사업 정밀 룰 (refs PDF cite)"],
      ["③ 기술성",
       "Gemini 2.5-flash 함수 호출 11 모듈 + LightGBM/GAT ablation + Prophet+LGBM stacking + 93,200 grid cache + BGE-m3 RAG + Microclimate downscaling"],
      ["④ 발전 가능성",
       "4-tier BM (B2C/B2G/B2B/정책 라이선스) 1년차 약 5.5억 + 산림 미래혁신센터 90억 결합 가능성 + 농림위성 CAS500-4 통합 로드맵"],
    ],
    [2500, 6860]
  ),
  PageBr(),
];

// ============================================================================
// 7. BM + 로드맵
// ============================================================================
const sec7 = [
  H1("7. 4-tier BM + 1년 로드맵"),
  H2("7.1 4-tier 사업 모델"),
  table(
    ["BM", "고객", "단가", "1년차 목표"],
    [
      ["B2C 매칭 수수료", "도시민 ↔ 산주·임차", "거래액 1~3%", "임야 거래 50건 × 평균 5천만 × 2% = 5,000만"],
      ["B2G 시군 SaaS", "시군 귀산촌 정책과", "군 단위 연 1억", "평창·영양·진안 3개 시군 = 3억"],
      ["B2B leads", "스마트팜 장비·종묘 업체", "건당 50만", "200건 = 1억"],
      ["정책 라이선스", "산림청·임업진흥원", "연 1억 (협의)", "1억"],
    ],
    [1800, 2200, 2000, 3360]
  ),
  P("1년차 총 매출 목표 약 5억 5,000만 원."),
  H2("7.2 1년 로드맵"),
  Bullet("8월 (M0): 시상 직후 + 4 페르소나 베타 + RAG corpus 일반 사용자 무료 베타"),
  Bullet("9~11월 (M1~M3): 시군 B2G 파일럿 (평창·영양·진안) → SaaS 첫 매출 3억"),
  Bullet("12~2월 (M4~M6): B2B leads 채널 구축 (영양 어수리 스마트팜 종묘) → 1억"),
  Bullet("3~5월 (M7~M9): 산림 미래혁신센터 90억 사업 결합 + 정책 라이선스 협의 + 농림위성 CAS500-4 36종 산출물 통합"),
  Bullet("6~7월 (M10~M12) 1주년: 4-tier BM 안정화 + KCI 산림과학회지 논문 투고 + 2027 본 대회 출품 검토"),
  PageBr(),
];

// ============================================================================
// 8. 마무리
// ============================================================================
const sec8 = [
  H1("8. 마무리 — 본 연구가 남기는 것"),
  P("본 연구는 단일 창업경진대회 출품작에 그치지 않는다. ForKG-Korea 라는 한국 산림 정책 지식그래프 인프라 (669 노드 + 962 엣지, ForPKG-1.0 한국 first application), 466 × 52 적합도 매트릭스 + 5년 Monte Carlo baseline 이라는 정량 baseline, 4 주관기관 데이터 + D:\\craft 17 source + 7,992 RAG 청크 통합이라는 데이터 과학 패턴은 모두 후속 연구와 정책 도구의 기초가 된다."),
  P("본 시스템이 우승하면 한국 산촌 인구 소멸과 사유림 영세화라는 가장 오래된 두 모순에 디지털 대응 도구가 처음으로 등장한다. 우승하지 못해도 학술 논문 (KCI 산림과학회지 또는 RecSys 워크숍) · MIT 오픈소스 코드 · 60 소스 데이터 인벤토리가 후속 연구자에게 남는다."),
  P("한국 산림 부문 디지털 의사결정 인프라의 첫 한 축 — 그것이 본 연구의 진짜 contribution이다.",
    { italics: true, color: FOREST_DEEP }),
  PageBr(),
];

// ============================================================================
// 참고 문헌
// ============================================================================
const refs = [
  H1("참고 문헌 (References)"),
  P("1. Sun, J., & Luo, Z. (2024). ForPKG-1.0: A Framework for Constructing Forestry Policy Knowledge Graph and Application Analysis. arXiv:2411.11090."),
  P("2. 한국임업진흥원. 임업정보 다드림 — 161종 산림 빅데이터 + 52품목 단기임산물 재배적지. gis.kofpi.or.kr/dad_user/"),
  P("3. 국립산림과학원. 산악기상관측망(KoMIS) — 480 지점 1분 단위 7항목. mtweather.nifos.go.kr"),
  P("4. 산림청. (2024). 2024 산촌기초조사 기준 전국 산촌 466 읍면 현황. (refs/02 추출 467 BJCD 정확 매칭)"),
  P("5. 산림청. (2026). 임업·산림 공익직접지불사업 시행지침 — 2026 임업직불금 532억원. (refs/05_direct_payment_guide_2026.pdf)"),
  P("6. 산림청. (2025). 산림소득분야 사업시행지침 — 표고 자목·톱밥배지 보조. (refs/04)"),
  P("7. 산림청. (2024). 산림사업종합자금 집행지침 — 귀산촌인 정책 융자. (refs/03)"),
  P("8. 산림청. (2025). 사회공헌형 산림탄소상쇄 운영표준 — KOC 등록 절차. (refs/09)"),
  P("9. 산림청·경상북도·영양군. (2026). 임산물 스마트팜 실증단지 105억 공모 계획. (refs/07)"),
  P("10. 기상청. (2025). 산악예보 API 활용가이드 + 단기예보 격자 위경도 lookup. (refs/06, 11, 12)"),
  P("11. 산림청. (2021). 산림소득지원사업 표준품셈 — M07 산촌체류형 쉼터 6항목 비용 baseline."),
  P("12. VWorld. 토지임야정보·연속지적도 OpenAPI (LP_PA_CBND_BUBUN, PNU 19자리). api.vworld.kr"),
  P("13. BGE-M3 (BAAI General Embedding). Multilingual SOTA dense retriever. huggingface.co/BAAI/bge-m3"),
  P("14. Google. Gemini 2.5-flash — Function calling, multilingual, long-context. ai.google.dev/gemini-api"),
  P("15. Hartman, R. (1976). The Harvesting Decision When a Standing Forest Has Value. Economic Inquiry, 14(1), 52–58."),
  P("16. Faustmann, M. (1849). On the Determination of the Value Which Forest Land and Immature Stands Possess for Forestry. (translated reprint, 1968)."),
];

// ============================================================================
// Build document
// ============================================================================
const doc = new Document({
  creator: "Heedo",
  title: "Soop Starter — 한국 산촌 청년 임업인 진입 의사결정 지원 시스템",
  description: "TR-2026-001 본 대회 출품 기획서 30p",
  styles: {
    default: { document: { run: { font: "Pretendard", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Noto Serif KR", color: FOREST_DEEP },
        paragraph: { spacing: { before: 360, after: 240 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Pretendard", color: BARK },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 22, bold: true, font: "Pretendard", color: FOREST_DEEP },
        paragraph: { spacing: { before: 180, after: 80 }, outlineLevel: 2 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets",
        levels: [{ level: 0, format: LevelFormat.BULLET, text: "•",
                   alignment: AlignmentType.LEFT,
                   style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: PAGE_W, height: PAGE_H },
        margin: { top: MARGIN, right: MARGIN, bottom: MARGIN, left: MARGIN },
      },
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: "Soop Starter · TR-2026-001",
                                  size: 16, color: BARK, font: "JetBrains Mono" })],
      })] }),
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [
          new TextRun({ text: "Page ", size: 16, color: BARK, font: "JetBrains Mono" }),
          new TextRun({ children: [PageNumber.CURRENT], size: 16, color: BARK, font: "JetBrains Mono" }),
          new TextRun({ text: " / ", size: 16, color: BARK, font: "JetBrains Mono" }),
          new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 16, color: BARK, font: "JetBrains Mono" }),
        ],
      })] }),
    },
    children: [
      ...cover, ...abstract, ...toc, ...sec1, ...sec2, ...sec3,
      ...sec4, ...sec5, ...sec6, ...sec7, ...sec8, ...refs,
    ],
  }],
});

const outDir = path.join(__dirname, "..", "data", "processed", "deliverables");
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });
const outPath = path.join(outDir, "soop_starter_proposal.docx");

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(outPath, buffer);
  console.log(`✓ ${outPath} (${(buffer.length / 1024).toFixed(0)} KB)`);
});
