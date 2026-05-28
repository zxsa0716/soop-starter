# API 운영계정 신청 가이드 — W1 첫날 즉시 진행

> **★ 가장 시간 critical** — 운영계정 승인까지 평균 1~3 영업일.
> 오늘 신청해야 W1 종료(05.18) 전에 W1-T3~T8 DAG가 실제 fetch 가능합니다.

이 문서는 `.env`의 **8개 키**를 한 번에 발급받는 순서입니다.

## 신청 순서 요약 (90분 작업)

| # | 서비스 | 발급 종류 | 소요 | 즉시? |
|---|---|---|---|---|
| 1 | **Anthropic Claude** | API Key | 5분 | ✅ 즉시 |
| 2 | **공공데이터포털 (data.go.kr)** | 회원가입 + 인증서 | 10분 | ✅ 즉시 |
| 3 | **산림자원통계 OpenAPI** | 운영계정 (data.go.kr) | 1~3 영업일 | ⏳ 대기 |
| 4 | **법제처 OpenAPI** | 사용자 OC (이메일 ID) | 즉시 | ✅ 즉시 |
| 5 | **VWorld OpenAPI** | 인증키 + 도메인 등록 | 즉시 | ✅ 즉시 |
| 6 | **KoMIS 산악기상** | 운영계정 + IP 등록 | 1~2 영업일 | ⏳ 대기 |
| 7 | **KOSIS / 기상청 / 토지실거래** | 운영계정 (data.go.kr) | 1~3 영업일 | ⏳ 대기 |
| 8 | **Google Earth Engine** | service account JSON | 30분~1일 | ⏳ 검토 |

---

## 1. Anthropic Claude API (★ 즉시)

1. https://console.anthropic.com/ 접속 → 가입
2. Settings → API Keys → "Create Key" → 이름 `soop-starter`
3. 발급된 `sk-ant-...` 키를 `.env`에 저장
4. **권장 credit**: 본선까지 최소 USD 100 충전 — Opus 4.7 함수 호출 11 모듈 + RAG 컨텍스트(약 30K tokens) × 4 페르소나 시연 × 반복 테스트

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-opus-4-7
```

## 2. 공공데이터포털 회원가입

1. https://www.data.go.kr/ → 회원가입 (개인, 휴대폰 인증)
2. 마이페이지 → 인증서 등록 (선택, 일부 API에서 요구)
3. 모든 data.go.kr 운영계정 신청은 여기서 진행

## 3. 산림자원통계 OpenAPI ⏳

본 시스템의 통계 backbone (임가경제 1,500가구 8업종 · 임산물생산 14종 145품목 · 임가소득 · 경영실태)

1. data.go.kr 로그인 → 데이터 검색 → "**산림자원통계 OpenAPI**" 검색
2. 또는 직접 이동: https://www.data.go.kr/data/15049890/openapi.do
3. 활용 신청 클릭 → **운영계정 신청서 작성**
   - 활용 목적: "한국 산촌 청년 임업인 진입 의사결정 지원 시스템 (2026 산림 공공데이터·AI 활용 창업경진대회 출품작) — 임가경제·임산물생산 통계를 다중모달 추천 파이프라인의 calibration prior로 활용"
   - 활용 시스템 구분: **웹 사이트 개발**
   - 라이선스 표시: 공공누리 4유형 (출처표시-상업적이용금지-변경금지) 동의
4. 일 트래픽 권장: **10,000건/일 이상** 신청
5. 승인 후 마이페이지 → 활용 → 인증키 복사 → `.env` `KFS_FRSAS1_KEY`

**End-point 확인**:
```
GET https://apis.data.go.kr/1400000/frsas1/getForestFamilyEconomyList?serviceKey=...
```

## 4. 법제처 국가법령정보 OpenAPI ✅

본 시스템 RAG corpus의 핵심 (산림자원법·임업산촌진흥촉진법·산지관리법·탄소흡수원법·임업산림직접지불제 운영법 5개 + 시행령·시행규칙·별표 전체)

1. https://open.law.go.kr/LSO/openApi/guideList.do
2. **OC = 이메일 형식 (사용자 ID)** — 가입·승인 불요, 즉시 사용 가능
3. `.env`에 다음 두 값 입력:
   ```bash
   LAW_GO_KR_OC=zxsa0716@kookmin.ac.kr   # 본인 이메일
   LAW_GO_KR_KEY=                          # 일부 endpoint는 키 추가 발급
   ```
4. 사용 가능 endpoint:
   - 법령 본문: `http://www.law.go.kr/DRF/lawService.do?OC=...&target=law&MST=...&type=XML`
   - 별표 서식: `http://www.law.go.kr/DRF/lawService.do?OC=...&target=licbyl&...`
   - 시행령: `target=lawjosub`

## 5. VWorld OpenAPI ✅ (★ M07 쉼터 입지 평가의 backbone)

토지임야·연속지적도(LP_PA_CBND_BUBUN)·공시지가·도로명주소

1. https://www.vworld.kr/dev/v4api.do → 회원가입
2. 인증키 발급 → 활용 → "**API 인증키 발급**"
   - 활용 URL/도메인: `localhost` (로컬 개발) + 향후 배포 도메인 추가
   - 일 트래픽: 30,000건 (개인 무료 한도)
3. `.env`:
   ```bash
   VWORLD_API_KEY=발급키
   VWORLD_DOMAIN=localhost
   ```
4. 사용 가능 서비스:
   - 토지임야: `https://api.vworld.kr/req/data?service=data&request=GetFeature&data=LP_PA_CBND_BUBUN&...`
   - 공시지가: `https://api.vworld.kr/req/data?...&data=LP_PA_CBND_BUBUN&attrFilter=jibun:LIKE:...`
   - WMS 타일: `https://api.vworld.kr/req/wmts/1.0.0/...` (Leaflet 지도 base)

## 6. 산악기상 KoMIS OpenAPI ⏳

본 시스템 시계열 backbone (480 지점 × 1분 단위 × 7항목 × 30년)

1. https://know.nifos.go.kr/openapi/mtweather/ 또는 https://mtweather.nifos.go.kr/
2. 회원가입 → OpenAPI 신청
3. **IP 등록 필수** — 개발 PC IP + 배포 서버 IP (Vercel/Render 사용 시 정적 IP 또는 Cloudflare 경유 필요)
4. 활용 목적: "산촌 청년 임업인 진입 의사결정 지원 — 466 산촌 5km 반경 microclimate downscaling 및 임산물 적합도 모델 산악기상 30년 평균 feature 활용"
5. `.env`: `KOMIS_API_KEY=`

**대안**: 일괄 다운로드 가능 시 MinIO에 적재 → API 미활용도 가능. W1-T8 참고.

## 7. 기타 data.go.kr 운영계정 (병렬 신청) ⏳

같은 양식으로 한 번에 신청해두면 W2 진입 시 모두 사용 가능:

- **KOSIS API** — `KOSIS_API_KEY` · https://kosis.kr/openapi/index/index.jsp
- **기상청 단기예보** — `KMA_GRID_API_KEY` · https://www.data.go.kr/data/15084084/openapi.do
- **국토부 토지 실거래가** — `REALESTATE_API_KEY` · https://www.data.go.kr/data/15126466/openapi.do
- **일별토지임야정보** — `KFS_PARCEL_DAILY_KEY` · https://www.data.go.kr/data/15045883/openapi.do
- **산림사업법인 OpenAPI** — `FOREST_BUSINESS_API_KEY` · https://www.data.go.kr/data/3071214/openapi.do
- **농진청 농산물 소득자료집** — https://www.data.go.kr/data/15123923 (51 작목 baseline)
- **법령 체계도 목록** — https://www.data.go.kr/data/15058790
- **2024 산촌 466 PDF** — 신청 불요, 다운로드만: forest.go.kr 통합자료실

## 8. Google Earth Engine ⏳ (Sentinel-2 NDVI/EVI 30y · GEDI · PALSAR-2)

1. https://earthengine.google.com/ → 가입
2. Cloud Project 생성 → Earth Engine API 활성화
3. **Service Account 생성**:
   - Cloud Console → IAM & Admin → Service Accounts → Create
   - Role: `Earth Engine Resource Viewer` + `Service Account User`
4. JSON 키 다운로드 → 프로젝트 루트에 `gee-service-account.json`으로 저장
5. `.env`:
   ```bash
   GEE_SERVICE_ACCOUNT_EMAIL=soop-starter@<project>.iam.gserviceaccount.com
   GEE_PROJECT_ID=<your-gcp-project>
   GEE_SERVICE_ACCOUNT_KEY_PATH=./gee-service-account.json
   ```
6. **Heedo 기존 GEE 자산 호환**: 본 시스템은 Sentinel-2 NDVI/EVI 30년 seasonality 계산 시 사용자의 기존 GEE 코드를 그대로 재활용합니다 (ml/m03_ndvi_seasonality.py).

## 9. 한국임업진흥원 다드림 (BYOA 패턴, 별도 발급 불요)

다드림은 사용자 본인이 다드림 웹에서 자기 임야 PNU를 조회 → 결과를 다드림 BYOA API로 우리 시스템에 인증된 form으로 전달합니다. 별도 API 신청 없이 사용자의 다드림 계정만 있으면 됩니다.

- 운영 URL: https://gis.kofpi.or.kr/dad_user/
- 신버전 (BYOA): https://neogis.kofpi.or.kr/dad_user
- 사용자 가이드: docs/05-personas.md 의 P-03 박재훈 시나리오 참고

---

## 즉시 체크리스트 (오늘 90분)

- [ ] Anthropic Claude 키 발급 → `.env` ANTHROPIC_API_KEY
- [ ] data.go.kr 회원가입 + 인증서
- [ ] 법제처 OC 입력 (`zxsa0716@kookmin.ac.kr`) → 즉시 테스트
- [ ] VWorld 인증키 + 도메인 등록 → 즉시 테스트
- [ ] data.go.kr 운영계정 일괄 신청: 산림자원통계 / KOSIS / 기상청 / 토지실거래 / 일별토지임야 / 산림사업법인 (6건 한 번에)
- [ ] KoMIS 운영계정 + IP 등록 신청
- [ ] Google Earth Engine service account JSON 생성

승인 대기 동안 W1-T1 (Docker 셋업), W1-T3 (FGIS 무료 신청 SHP — 별도 API 불요), 그리고 ForKG-Korea ontology 작성을 병행합니다.

---

## 즉시 테스트 가능한 endpoint 체크

`.env`에 키를 채운 직후 다음 명령으로 4개를 빠르게 검증:

```bash
# 법제처 — OC만으로 즉시 가능
curl "http://www.law.go.kr/DRF/lawService.do?OC=${LAW_GO_KR_OC}&target=law&MST=234829&type=XML" | head -c 500

# VWorld — 인증키 발급 직후 가능
curl "https://api.vworld.kr/req/data?service=data&request=GetFeature&data=LP_PA_CBND_BUBUN&key=${VWORLD_API_KEY}&domain=${VWORLD_DOMAIN}&geomFilter=POINT(127.0276%2037.4979)&size=1"

# Anthropic — 즉시 가능
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: ${ANTHROPIC_API_KEY}" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{"model":"claude-opus-4-7","max_tokens":32,"messages":[{"role":"user","content":"ping"}]}'

# 산림자원통계 (승인 후)
curl "https://apis.data.go.kr/1400000/frsas1/getForestFamilyEconomyList?serviceKey=${KFS_FRSAS1_KEY}&numOfRows=1&pageNo=1"
```

승인된 키는 `scripts/secret_rotate.sh`로 7일마다 자동 검증·회전.
