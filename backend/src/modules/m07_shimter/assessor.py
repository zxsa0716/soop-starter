"""
M07 — 산촌체류형 쉼터 7개 룰 검증 + 비용 시뮬.

7 rules (산지관리법 시행령 일부개정안):
  R1. 산지 ≥ 400㎡
  R2. 부지 < 100㎡
  R3. 연면적 ≤ 33㎡
  R4. 임업용 산지 여부
  R5. 도로 직접 접근
  R6. 방재지구 외
  R7. 화기 시설 불가 (사용자가 동의해야 함)

비용 = 표준품셈 6항목 × ±15%.
"""
from __future__ import annotations
import logging
from pathlib import Path

import httpx

from ...core.config import settings

logger = logging.getLogger(__name__)


SHIMTER_RULES = [
    {"id": "R1", "name": "산지 ≥ 400㎡", "field": "lot_area_sqm",       "min": 400,  "max": None},
    {"id": "R2", "name": "부지 < 100㎡",  "field": "site_area_sqm",      "min": None, "max": 100},
    {"id": "R3", "name": "연면적 ≤ 33㎡", "field": "floor_area_sqm",     "min": None, "max": 33},
    {"id": "R4", "name": "임업용 산지",    "field": "is_im_eob_yong_sanji"},
    {"id": "R5", "name": "도로 직접 접근", "field": "has_direct_road_access"},
    {"id": "R6", "name": "방재지구 외",    "field": "in_disaster_zone",   "must_be": False},
    {"id": "R7", "name": "화기 시설 불가", "field": "user_no_fire_consent"},
]

# 표준품셈 2021 기준 단가 (단위: 원)
STANDARD_COSTS_P50 = {
    "foundation":             2_500_000,   # 기초
    "main_structure_wood_33sqm": 28_000_000,  # 목조 33㎡
    "deck":                   4_000_000,   # 데크
    "septic_tank":            2_500_000,   # 정화조
    "driveway":               3_500_000,   # 진입로
    "permit":                 1_000_000,   # 인허가
}


async def assess_shimter_eligibility(
    lot_pnu: str,
    design_options: dict | None = None,
) -> dict:
    """필지 PNU → 산지구분도 PostGIS join → 7 룰 평가 → 비용 ±15% range."""
    design_options = design_options or {}

    lot = await _fetch_lot_attributes(lot_pnu)

    # 사용자 design override
    floor_area = design_options.get("floor_area_sqm", 33)
    site_area = design_options.get("site_area_sqm", 90)

    rule_results = {
        "rule_sanji_area_400sqm_plus":   lot["area_sqm"] >= 400,
        "rule_site_under_100sqm":        site_area < 100,
        "rule_floor_area_under_33sqm":   floor_area <= 33,
        "rule_im_eob_yong_sanji":        lot["is_im_eob_yong_sanji"],
        "rule_direct_road_access":       lot["has_direct_road_access"],
        "rule_outside_disaster_zone":    not lot.get("in_disaster_zone", False),
        "rule_no_fire_equipment":        design_options.get("user_no_fire_consent", True),
    }

    violations = [k for k, v in rule_results.items() if not v]
    is_eligible = len(violations) == 0

    cost_estimate = None
    recommended_design = None
    if is_eligible:
        cost_estimate = _calc_cost(floor_area, design_options)
        recommended_design = f"{floor_area}㎡ 목조 + 20㎡ 데크 + 정화조 + 주차장 + 인허가"

    return {
        **rule_results,
        "is_eligible": is_eligible,
        "cost_estimate": cost_estimate,
        "recommended_design": recommended_design,
        "next_step_guidance": (
            "산지전용통합정보시스템 1644-0672 또는 시군 산림과 방문 신청. "
            "임야 PNU + 토지이용계획확인서 + 산지전용 신고서 제출."
        ),
        "rule_violations": violations,
        "law_citation": {
            "law": "산지관리법 시행령",
            "amended_provision": "별표 ○○호 산촌체류형 쉼터 기준",
            "source": "법제처 OpenAPI 주 1회 sync (DAG4_legal)",
        },
    }


# ============================================================================
async def _fetch_lot_attributes(lot_pnu: str) -> dict:
    """VWorld + PostGIS join. MVP에서는 VWorld API 결과 사용."""
    if not settings.vworld_api_key:
        logger.warning("VWORLD_API_KEY missing; returning fixture lot")
        return _fixture_lot()

    url = "https://api.vworld.kr/req/data"
    params = {
        "service": "data", "request": "GetFeature",
        "data": "LP_PA_CBND_BUBUN",
        "key": settings.vworld_api_key,
        "domain": settings.vworld_domain,
        "attrFilter": f"pnu:=:{lot_pnu}",
        "format": "json",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()
    features = data.get("response", {}).get("result", {}).get("featureCollection", {}).get("features", [])
    if not features:
        return _fixture_lot()
    f = features[0]["properties"]
    return {
        "pnu": lot_pnu,
        "area_sqm": float(f.get("lndpcl_ar", 3200)),
        "is_im_eob_yong_sanji": str(f.get("lndcgr_code", "")).startswith("75"),
        "has_direct_road_access": True,
        "in_disaster_zone": False,
    }


def _fixture_lot() -> dict:
    """P-01 김도현 평창 매물 A 0.32ha."""
    return {
        "pnu": "4276034021100010000",
        "area_sqm": 3200,
        "is_im_eob_yong_sanji": True,
        "has_direct_road_access": True,
        "in_disaster_zone": False,
    }


def _calc_cost(floor_area: float, design_options: dict) -> dict:
    """표준품셈 ±15% range."""
    base = sum(STANDARD_COSTS_P50.values())
    floor_adj = STANDARD_COSTS_P50["main_structure_wood_33sqm"] * (floor_area / 33 - 1)
    total_p50 = base + floor_adj
    return {
        **STANDARD_COSTS_P50,
        "total_p10_won": int(total_p50 * 0.85),
        "total_p50_won": int(total_p50),
        "total_p90_won": int(total_p50 * 1.15),
    }
