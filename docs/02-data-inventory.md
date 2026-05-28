# 데이터 인벤토리 — 60 소스 카탈로그

> 약 60개 검증 소스 → 25개 핵심 backbone + 35개 보조.
> **전부 무료 또는 개인 신청만으로 접근 가능, 협업 공문 불요.**

## ① 산림청 본청 (9종) → M02 M03 M05 M06 M07 M08 M10

| 데이터셋 | URL | 활용 모듈 | 비고 |
|---|---|---|---|
| 산림자원통계 OpenAPI | apis.data.go.kr/1400000/frsas1 | M03 M05 | 임가경제·임산물생산·생산비·소득·경영실태 통합 |
| 산림임업통계플랫폼 | kfss.forest.go.kr | M03 | NFI 5~7차 임분조사표 마이크로데이터 |
| NFI 마이크로데이터 | data.go.kr/data/15122903 | M03 | 16만 표본 점 CSV |
| FGIS 산림공간정보 | map.forest.go.kr | M02 M03 M07 | 임상도·토양도·산지구분도·산림이용기본도 SHP 무료 신청 |
| 임업-in 통합포털 | foco.go.kr / pay.foco.go.kr | M06 | 직불금 + 경영체 + 사업지원 + 가격동향 |
| 산림교육원 | fhi.forest.go.kr | M09 | 임업후계자 양성과정 일정 (크롤) |
| 산림탄소상쇄제도 | forest.go.kr (042-603-7315) | M06 | KOC 등록부 + 검·인증 |
| 2024 산촌 466 PDF | forest.go.kr 통합자료실 | M02 | 433KB · 산림기본법 §3 분류 |
| 산림소득지원사업 표준품셈 2021 | files-scs.pstatic.net | M05 M07 | 약초·약용·표고종균접종 단가 |

## ② 한국임업진흥원 (6종, 정수민 위원 직접 운영) → M03 M05 M06 M09 M11

| 데이터셋 | URL | 활용 모듈 | 비고 |
|---|---|---|---|
| **임업정보 다드림** | gis.kofpi.or.kr/dad_user/ | M03 M05 | ★ **161종 산림 빅데이터 + 52품목 재배적지** (backbone) |
| 다드림 신버전 BYOA | neogis.kofpi.or.kr/dad_user | M03 M07 | 사용자 본인 인증 후 자기 데이터 가져오기 |
| 산림빅데이터거래소 | bigdata-forest.kr | M02 M03 | 산촌지도·숲세권·임산물 트렌드 |
| 거래소 시각화 포털 | gis.forestdata.kr | M02 | 104개 산촌마을 좌표 (2018) |
| 산림사업법인 OpenAPI | data.go.kr/data/3071214 | M09 | 등록번호·대표·기술능력·상벌 |
| 산림형 예비사회적 기업 | kofpi.or.kr | M09 | 멘토십 옵션 |

## ③ 한국산림복지진흥원 → M02 M11

| 데이터셋 | URL | 비고 |
|---|---|---|
| 전국 치유의숲 좌표 | data.go.kr/data/15110279 | 위경도 포함 무료 |
| 전국휴양림표준데이터 | data.go.kr/data/15013111 | 자연휴양림 위치·시설·운영 |
| 숲e랑 서비스 | fowi.or.kr | 산림복지 서비스 검색 |

## ④ 한국등산·트레킹지원센터 → M02 M11

| 데이터셋 | URL | 비고 |
|---|---|---|
| 전국 봉우리 POI | data.go.kr/data/15108062 | 위경도 + 높이 |
| 숲길 편의시설 POI | data.go.kr/data/15125108 | 화장실·쉼터·이정표 |
| 숲서비스·둘레길 정보 | data.go.kr/data/15002725 | GPX/SHP 거리·시간 포함 |

## ⑤ 산림과학원 산악기상 + 위성

| 데이터셋 | URL | 활용 모듈 | 비고 |
|---|---|---|---|
| KoMIS 산악기상관측망 | mtweather.nifos.go.kr | M03 M10 | 480 지점 · 1분 · 7항목 · QC 98% |
| 산악기상 OpenAPI | know.nifos.go.kr/openapi/mtweather/ | M10 | 지점 list + 시점별 관측값 |
| 기상청 단기예보 | data.go.kr/data/15084084 | M10 | 5km 격자 동네예보 |
| Sentinel-2 (Earth Engine) | code.earthengine.google.com | M03 | NDVI/EVI 30년 시계열 (Heedo GEE 자산) |
| GEDI L4A | NASA via GEE | M03 | 산림 바이오매스 25m bin |
| ALOS PALSAR-2 | JAXA mosaic via GEE | M03 | L-band SAR 산림 구조 |

> **농림위성 CAS500-4 (2026 초 발사 예정)** 36종 산림 활용 산출물은 발사 안정화 시점이 발표일과 겹치므로 MVP 제외, 향후 로드맵으로 분리.

## ⑥ 외부 정부 데이터 → M07 매물 매칭 + RAG

| 데이터셋 | URL | 활용 모듈 | 비고 |
|---|---|---|---|
| VWorld OpenAPI | api.vworld.kr | M07 | 토지임야·공시지가·연속지적도(LP_PA_CBND_BUBUN) 일 30,000건 무료 |
| 국토부 토지 실거래가 | data.go.kr/data/15126466 | M07 | OpenAPI · 법정동코드+계약년월 |
| 일별토지임야정보 | data.go.kr/data/15045883 | M07 | CSV 일별 갱신 |
| 산림조합 임야거래장터 | iforest.nfcf.or.kr | M07 M09 | 공식 직거래 (robots.txt 준수 크롤) |
| KOSIS API | kosis.kr/openapi | M02 | 임가경제 + 농가소득 + 인구 + 고령화 |
| 농진청 농산물 소득자료집 | amis.rda.go.kr · data.go.kr/data/15123923 | M05 | 51 작목 비교 baseline |
| 법제처 OpenAPI | open.law.go.kr/LSO/openApi | M06 M08 | 법률·시행령·시행규칙·별표 전체 |
| 법령 체계도 목록 | data.go.kr/data/15058790 | M08 | 법률 간 관계 |

## 통계

```
산림청 본청        9
한국임업진흥원      6
복지진흥원         3
등산트레킹센터      3
산림과학원 산악기상   2
위성             3
외부 정부         8
학술자료(ForPKG 등) +5
─────────────────────
검증 backbone      39
+ 보조/참고        21
─────────────────────
총                60
```

## ETL 6 DAG 매핑

| DAG | 주기 | 입력 데이터 | 출력 |
|---|---|---|---|
| dag1_static_shp | 월 | FGIS 4종 + 466 boundary | PostGIS 테이블 4종 (SRID 5179, GIST) |
| dag2_statistics | 월 | 산림자원통계 API + KOSIS + 농진청 51 작목 | DuckDB stats.db + 8업종 분포 JSON |
| dag3_realtime | 시간 | KoMIS + 기상청 + 산불/산사태 + 임업비서 가격 | Redis (7d TTL) |
| dag4_legal | 주 | 법제처 5법령 + 시행지침서 PDF + 시군 조례 | corpus_legal/ 3,000 청크 → Chroma |
| dag5_earth_engine | 월 | Sentinel-2 + GEDI + PALSAR (Heedo GEE) | ndvi_seasonality.parquet (466 × 12 × 30y) |
| dag6_model_retrain | 월 | features.parquet 갱신 | LGBM/KNN/GAT/Prophet .pkl + income_grid.duckdb (93k) |
