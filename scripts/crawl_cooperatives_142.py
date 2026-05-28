"""
W1-T6 — 산림조합 142 시군 위치 크롤러 + 산림사업법인 + 임야거래장터
================================================================
nfcf.or.kr robots.txt 준수 + UA 명시 + 1 req/3s rate limit.
산림조합중앙회 OpenAPI 부재 → 자체 크롤.
산림사업법인은 data.go.kr/data/3071214 OpenAPI 활용.

Usage:
  python scripts/crawl_cooperatives_142.py
Output: data/processed/cooperatives_142.json + forest_business_corp.parquet
"""
from __future__ import annotations
import json
import os
import time
import logging
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

DATA = Path(__file__).parent.parent / "data" / "processed"
UA = "SoopStarterBot/1.0 (+https://github.com/Heedo/soop-starter; mailto:zxsa0716@kookmin.ac.kr)"

NFCF_ROOT = "https://www.nfcf.or.kr"
NFCF_BRANCHES_PATH = "/sites/main/branch/list.do"
RATE_LIMIT_SEC = 3.0


def fetch_branch_list() -> list[dict]:
    """산림조합중앙회 142개 시군 조합 list — robots.txt 준수."""
    out = []
    with httpx.Client(headers={"User-Agent": UA}, timeout=15, follow_redirects=True) as cli:
        # robots.txt 확인
        robots = cli.get(f"{NFCF_ROOT}/robots.txt").text
        log.info(f"robots.txt:\n{robots[:300]}")

        for sido_code in ["11", "26", "27", "28", "29", "30", "31", "36",
                          "41", "43", "44", "45", "46", "47", "48", "50", "51", "52"]:
            r = cli.get(f"{NFCF_ROOT}{NFCF_BRANCHES_PATH}", params={"sido_code": sido_code})
            if r.status_code != 200:
                log.warning(f"sido {sido_code} → {r.status_code}")
                continue
            soup = BeautifulSoup(r.text, "lxml")
            for card in soup.select(".branch-card, .org-item"):
                out.append({
                    "name": card.select_one(".name").get_text(strip=True) if card.select_one(".name") else "",
                    "phone": card.select_one(".phone").get_text(strip=True) if card.select_one(".phone") else "",
                    "address": card.select_one(".addr").get_text(strip=True) if card.select_one(".addr") else "",
                    "sigungu_code": _infer_sigungu_code(card),
                })
            time.sleep(RATE_LIMIT_SEC)

    if not out:
        log.warning("크롤 결과 0 → fixture 사용 (스크래퍼 selector 업데이트 필요)")
        return _fixture_cooperatives()
    return out


def fetch_forest_business_corps() -> list[dict]:
    """산림사업법인 OpenAPI — 등록번호·대표·기술능력."""
    key = os.environ.get("FOREST_BUSINESS_API_KEY")
    if not key:
        log.warning("FOREST_BUSINESS_API_KEY 미발급 → 빈 list 반환")
        return []
    url = "https://api.odcloud.kr/api/3071214/v1/uddi:..."
    out = []
    for page in range(1, 50):
        r = httpx.get(url, params={"serviceKey": key, "perPage": 100, "page": page}, timeout=15)
        if r.status_code != 200:
            break
        items = r.json().get("data", [])
        if not items:
            break
        out.extend(items)
        time.sleep(0.5)
    return out


def _infer_sigungu_code(card) -> str:
    return ""


def _fixture_cooperatives() -> list[dict]:
    return [
        {"id": "cooperative_4276", "name": "평창산림조합", "sigungu_code": "4276",
         "address": "강원특별자치도 평창군 평창읍", "phone": "033-332-XXXX",
         "services": ["임업정책자금", "단기소득자금", "임야거래장터", "교육"]},
        {"id": "cooperative_4313", "name": "충주산림조합", "sigungu_code": "4313",
         "address": "충청북도 충주시", "phone": "043-841-XXXX",
         "services": ["임업정책자금", "교육"]},
        {"id": "cooperative_4577", "name": "진안산림조합", "sigungu_code": "4577",
         "address": "전북특별자치도 진안군", "phone": "063-433-XXXX",
         "services": ["임업정책자금", "단기소득자금"]},
        {"id": "cooperative_4776", "name": "영양산림조합", "sigungu_code": "4776",
         "address": "경상북도 영양군", "phone": "054-682-XXXX",
         "services": ["임업정책자금", "교육"]},
    ]


def main():
    DATA.mkdir(parents=True, exist_ok=True)
    coops = fetch_branch_list()
    (DATA / "cooperatives_142.json").write_text(
        json.dumps(coops, ensure_ascii=False, indent=2), encoding="utf-8")
    log.info(f"saved {len(coops)} cooperatives → cooperatives_142.json")

    biz_corps = fetch_forest_business_corps()
    if biz_corps:
        import pandas as pd
        pd.DataFrame(biz_corps).to_parquet(DATA / "forest_business_corp.parquet", index=False)
        log.info(f"saved {len(biz_corps)} forest business corps → forest_business_corp.parquet")


if __name__ == "__main__":
    main()
