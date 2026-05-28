# 배포 — GitHub + Vercel + Render

## 본 대회 제출 5종 패키지

| # | 항목 | 위치 |
|---|---|---|
| ① | 기획서 PDF 30p | `docs/proposal.pdf` (별도 빌드) |
| ② | GitHub repo | `https://github.com/<user>/soop-starter` |
| ③ | 라이브 데모 URL | `https://soop-starter.vercel.app` |
| ④ | 데모 영상 30초 | `docs/demo_30sec.mp4` |
| ⑤ | 본선 발표 슬라이드 30장 | `soop_starter_slides.html` 또는 PPTX |

## Frontend → Vercel

```bash
cd frontend
npx vercel link
npx vercel --prod
```

`vercel.json` 없이 Next.js 15 standalone build로 자동 인식.
환경 변수: `NEXT_PUBLIC_API_URL` = backend Render URL.

## Backend → Render (Web Service)

```yaml
# render.yaml
services:
  - type: web
    name: soop-backend
    runtime: docker
    dockerfilePath: ./backend/Dockerfile
    dockerContext: ./backend
    plan: standard
    envVars:
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: POSTGRES_HOST
        fromDatabase: { name: soop-db, property: host }
      # ...
databases:
  - name: soop-db
    plan: starter
    postgresMajorVersion: 16
```

## 정적 자산 → MinIO 또는 R2

KoMIS 200GB raw, Chroma 임베딩 등은 별도 S3 호환 저장소 권장. Render 디스크 제한 (10GB) 회피.

## 시연 안정성 — 3중 안전장치 (★ 발표 당일)

1. **사전 계산 grid 캐시** (`data/processed/income_grid.duckdb`, 93,000 시나리오)
2. **4 페르소나 hard-coded fallback** (`data/fixtures/persona_p0[1-4].json`)
3. **외부 API 7일 TTL Redis 캐시** (KoMIS·VWorld·법제처)

추가로: **30초 사전 녹화 데모 영상** (`docs/demo_30sec.mp4`) — 모든 API·LLM·네트워크 장애에도 시연 가능.

## 24/7 health check

```bash
# Vercel
curl https://soop-starter.vercel.app/api/health

# Render
curl https://soop-backend.onrender.com/health
```

CI에서 push마다 양쪽 자동 ping → Slack/Discord webhook 알림 (선택).

## 비용 추정 (본선 1개월)

| 항목 | 단가 | 월 예상 |
|---|---|---|
| Vercel Hobby | $0 | $0 |
| Render Standard | $25/mo | $25 |
| Render Postgres Starter | $7/mo | $7 |
| Anthropic Claude (Opus 4.7) | 시연 ~500회 | $40~80 |
| Cloudflare R2 (200GB) | $3/mo | $3 |
| 도메인 (선택) | $12/yr | $1 |
| **합계** | | **약 $80/월** |

대회 종료 후 운영비를 4-tier BM (B2C+B2G+B2B+정책 라이선스) 1년차 약 5.5억 매출로 자급화.
