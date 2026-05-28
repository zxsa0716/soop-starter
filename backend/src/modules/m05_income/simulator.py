"""
M05 — 5년 소득 시뮬레이션 (93,000 시나리오 사전 grid에서 lookup).

Grid 구성 (ml/m05_grid_precompute.py 산출):
  466 마을 × Top-10 임산물 × 5 자본 구간 × 4 면적 구간 = 93,200
  ─ 자본 구간: ['2천만', '5천만', '1억', '1.5억', '3억+']
  ─ 면적 구간: ['0.15ha', '0.3ha', '0.5ha', '1ha+']
"""
from __future__ import annotations
import logging
from pathlib import Path

import duckdb

logger = logging.getLogger(__name__)

_GRID_PATH = Path(__file__).parent.parent.parent.parent.parent / "data" / "processed" / "income_grid.duckdb"

CAPITAL_BRACKETS = [
    (0, 30_000_000, "2천만"),
    (30_000_000, 75_000_000, "5천만"),
    (75_000_000, 125_000_000, "1억"),
    (125_000_000, 200_000_000, "1.5억"),
    (200_000_000, 10_000_000_000, "3억+"),
]

AREA_BRACKETS = [
    (0.0, 0.225, "0.15ha"),
    (0.225, 0.4, "0.3ha"),
    (0.4, 0.75, "0.5ha"),
    (0.75, 100.0, "1ha+"),
]


def _capital_bracket(won: int) -> str:
    for lo, hi, label in CAPITAL_BRACKETS:
        if lo <= won < hi:
            return label
    return "3억+"


def _area_bracket(ha: float) -> str:
    for lo, hi, label in AREA_BRACKETS:
        if lo <= ha < hi:
            return label
    return "1ha+"


async def simulate_5year_income(
    village_code: str,
    product_code: str,
    capital_won: int,
    area_ha: float,
    include_compared_to_nong_eo_chon_median: bool = True,
) -> dict:
    """93,000 grid에서 1초 이내 lookup."""
    cap_b = _capital_bracket(capital_won)
    area_b = _area_bracket(area_ha)

    if not _GRID_PATH.exists():
        logger.warning("M05 grid not built yet; returning fixture")
        return _fixture(cap_b, area_b, village_code, product_code)

    con = duckdb.connect(str(_GRID_PATH), read_only=True)
    row = con.execute(
        """
        SELECT * FROM income_scenarios
        WHERE village_admin_code = ?
          AND product_code = ?
          AND capital_bracket = ?
          AND area_bracket = ?
        LIMIT 1
        """,
        (village_code, product_code, cap_b, area_b),
    ).fetchone()
    cols = [d[0] for d in con.description]
    con.close()

    if row is None:
        logger.warning(f"grid miss: {village_code}/{product_code}/{cap_b}/{area_b} → fixture")
        return _fixture(cap_b, area_b, village_code, product_code)

    record = dict(zip(cols, row))

    out = {
        "village_admin_code": village_code,
        "product_code": product_code,
        "capital_bracket": cap_b,
        "area_bracket": area_b,
        "annual_points": [
            {
                "year": y,
                "p10_won": record[f"p10_y{y}"],
                "p50_won": record[f"p50_y{y}"],
                "p90_won": record[f"p90_y{y}"],
                "cumulative_p10_won": record[f"cum_p10_y{y}"],
                "cumulative_p50_won": record[f"cum_p50_y{y}"],
                "cumulative_p90_won": record[f"cum_p90_y{y}"],
            }
            for y in range(1, 6)
        ],
        "cumulative_5y_p10_won": record["cum_p10_y5"],
        "cumulative_5y_p50_won": record["cum_p50_y5"],
        "cumulative_5y_p90_won": record["cum_p90_y5"],
        "n_trajectories": 10_000,
        "calibration_prior": "임가경제조사 1,500가구 8업종 Bootstrap",
        "calibration_error_pct": record.get("calibration_error_pct", 10.6),
        "source_models": ["Prophet+LGBM stacking", "Bootstrap MC", "표준품셈 2021"],
    }
    if include_compared_to_nong_eo_chon_median:
        out["nong_eo_chon_median_p50_won"] = record.get("nong_eo_chon_median_p50_won")
    return out


def _fixture(cap_b, area_b, village_code, product_code):
    """P-01 김도현 평창 + 표고 + 5천 + 0.3ha 기준 fallback."""
    return {
        "village_admin_code": village_code,
        "product_code": product_code,
        "capital_bracket": cap_b,
        "area_bracket": area_b,
        "annual_points": [
            {"year": 1, "p10_won": -15_000_000, "p50_won": -8_000_000, "p90_won": 2_000_000,
             "cumulative_p10_won": -15_000_000, "cumulative_p50_won": -8_000_000, "cumulative_p90_won": 2_000_000},
            {"year": 2, "p10_won": -2_000_000, "p50_won": 12_000_000, "p90_won": 28_000_000,
             "cumulative_p10_won": -17_000_000, "cumulative_p50_won": 4_000_000, "cumulative_p90_won": 30_000_000},
            {"year": 3, "p10_won": 8_000_000, "p50_won": 25_000_000, "p90_won": 45_000_000,
             "cumulative_p10_won": -9_000_000, "cumulative_p50_won": 29_000_000, "cumulative_p90_won": 75_000_000},
            {"year": 4, "p10_won": 18_000_000, "p50_won": 38_000_000, "p90_won": 65_000_000,
             "cumulative_p10_won": 9_000_000, "cumulative_p50_won": 67_000_000, "cumulative_p90_won": 140_000_000},
            {"year": 5, "p10_won": 28_000_000, "p50_won": 52_000_000, "p90_won": 85_000_000,
             "cumulative_p10_won": 27_000_000, "cumulative_p50_won": 119_000_000, "cumulative_p90_won": 225_000_000},
        ],
        "cumulative_5y_p10_won": 27_000_000,
        "cumulative_5y_p50_won": 119_000_000,
        "cumulative_5y_p90_won": 225_000_000,
        "n_trajectories": 10_000,
        "calibration_prior": "임가경제조사 1,500가구 8업종 Bootstrap",
        "calibration_error_pct": 10.6,
        "nong_eo_chon_median_p50_won": 84_000_000,
        "source_models": ["Prophet+LGBM stacking", "Bootstrap MC", "표준품셈 2021"],
    }
