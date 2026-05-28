# Soop Starter v3 — 산촌 진입 의사결정 시스템

**한국 산림 공공데이터·AI 활용 창업경진대회 2026**

## 빠른 실행 (Windows)

### 방법 1: 더블클릭 (추천)
파일 탐색기에서 `RUN_DEMO.bat` 더블클릭

### 방법 2: 명령 프롬프트
```cmd
cd E:\forestLLM\streamlit_app
pip install -r requirements.txt
set GEMINI_API_KEY=AIzaSy...
streamlit run soop_app.py
```

→ 브라우저에서 자동으로 http://localhost:8501 열림

## 9가지 모드

| 모드 | 설명 |
|---|---|
| 💬 **대화 (메인)** | 자연어 입력 → 8 모듈 자동 streaming → 통합 결정 대시보드 |
| 👤 페르소나 비교 | 4 페르소나 동시 비교 fan chart |
| 🗺️ 산촌 지도 | Folium 인터랙티브 (467 산촌 + 4 페르소나) |
| 🌳 ForKG 탐색 | 729 노드 정책 KG · focus + hop slider |
| 💰 임산물 비교 | 10 임산물 ROI Calculator |
| 🎚️ 민감도 분석 | 5 slider 실시간 MC 시뮬레이션 |
| 📚 RAG 정책 질의 | Gemini 2.5-flash + 인용 강제 가드레일 |
| 📊 실 학습 결과 | M03/M04/M05/Latency 인터랙티브 차트 |
| ℹ️ About | 학술 기여 + 검증 결과 |

## 💬 대화 모드 사용법 (메인)

1. 샘플 4개 중 하나 선택 (또는 "직접 입력")
2. "실 Gemini 호출" 체크박스
   - **OFF (fixture)**: 즉시 실행 (시연용)
   - **ON (실 Gemini)**: 8-10초 실 호출
3. "🚀 의사결정 파이프라인 실행" 클릭
4. Progress bar로 M01→M09 streaming 진행
5. 통합 대시보드 한 화면에 모든 결과 등장:
   - 4 stat cards (5y P50 / Top 임산물 / 거점 / 쉼터)
   - Fan chart (5y P10/P50/P90)
   - Radar (4축 평가)
   - Sankey diagram (의사결정 흐름)
   - Treemap (보조사업 amount)
   - Top-3 추천 임산물
   - 이번 주 액션 아이템
   - Folium 지도 (focus 페르소나 강조)
6. **결정 패키지 JSON 다운로드** 버튼으로 공유 가능

## 자동 페르소나 매칭

자연어 입력 → 자동으로 4 페르소나 중 가장 가까운 것 매칭:

| 입력 키워드 | 매칭 |
|---|---|
| "강원", "평창", "표고" | P-01 김도현 |
| "충북", "충주", "수안보", "산양삼" | P-02 이수진 |
| "전북", "진안", "탄소", "KOC" | P-03 박재훈 |
| "경북", "영양", "스마트팜" | P-04 정민호 |
| 키워드 없으면 | 자본 기준 fallback |

## 학술 결과 (실 학습)

- **M03 LightGBM**: NFI 7 12,331 표본점 · Mean Test R² = **0.580**
- **M04 ForKG Node2Vec**: 729/993 graph · P@5 = **0.857**, MRR 0.523
- **M05 Holt+LGBM Stacking**: 178 시군구 · MAPE 93.4% → **72.5%** (+22.3%)
- **Latency**: 직렬 20s / 병렬 **10.3s** / Streaming 첫 byte 2s

## 패키지 구조

```
streamlit_app/
├── soop_app.py            (974 lines, 9 modes)
├── requirements.txt       (folium + plotly + lightgbm 포함)
├── RUN_DEMO.bat           (Windows 더블클릭 실행)
├── README.md              (이 파일)
└── data/                  (자동 로드)
    ├── fixtures/persona_p0[1-4].json  (4 페르소나 fixture)
    └── processed/
        ├── sanchon_466_official.json  (467 villages)
        ├── products_top10.json
        ├── persona_grid_official.json
        ├── forkg_korea/forkg_korea_v2.json
        ├── m03_real/m03_metrics.json + .pkl
        ├── m04_real/m04_metrics.json + .npy
        ├── m05_real/m05_metrics.json
        └── latency_real/latency_metrics.json
```

E:\forestLLM\data\ 폴더에서 자동 로드 (streamlit_app 폴더 안에 data가 없으면 상위에서 찾음).

## 검증 통과

- ✅ Streamlit boot `/_stcore/health = ok`
- ✅ 8/8 페르소나 자동 매칭 시나리오
- ✅ Plotly Sankey + Treemap + Folium 지도 정상
- ✅ 결정 패키지 JSON 다운로드 동작
- ✅ M01 (Gemini 27 fields) + M08 (RAG 인용 강제) 실 호출 검증

Heedo · 국민대학교 · TR-2026-001 · 2026-06-19 18:00 제출
