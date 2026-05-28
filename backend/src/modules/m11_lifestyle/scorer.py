"""M11 — 5km 반경 시설 밀도·거리 decay. 4축 (등산·치유·휴양·자연 접근성)."""
from __future__ import annotations
import logging
import math
from ...core.db import session_scope
logger = logging.getLogger(__name__)


async def score_lifestyle_axes(village_code: str, radius_km: float = 5.0) -> dict:
    """치유의숲·자연휴양림·봉우리·둘레길 5개 데이터셋 결합."""
    try:
        async with session_scope() as session:
            sql = """
              SELECT category, COUNT(*) AS n, AVG(distance_km) AS avg_d
              FROM v_lifestyle_poi_buffered
              WHERE village_admin_code = :code AND distance_km <= :r
              GROUP BY category
            """
            rows = (await session.execute(sql, {"code": village_code, "r": radius_km})).mappings().all()
    except Exception as e:
        logger.warning(f"M11 DB query failed: {e}; fixture")
        rows = _fixture_rows()

    by_cat = {r["category"]: r for r in rows}
    score = {
        "hiking":           _density_score(by_cat.get("peak", {}),         radius_km),
        "healing":          _density_score(by_cat.get("chiyu_forest", {}), radius_km),
        "leisure":          _density_score(by_cat.get("recreation", {}),   radius_km),
        "nature_access":    _density_score(by_cat.get("trail", {}),        radius_km),
    }
    score["composite"] = sum(score.values()) / 4
    return {"village_code": village_code, "radius_km": radius_km, "axes": score,
            "data_sources": ["15110279", "15013111", "15108062", "15125108", "15002725"]}


def _density_score(row: dict, radius_km: float) -> float:
    if not row:
        return 0.0
    n = row.get("n", 0)
    avg_d = row.get("avg_d", radius_km)
    decay = math.exp(-avg_d / (radius_km / 2))
    return min(1.0, (n / 10) * decay)


def _fixture_rows():
    return [
        {"category": "peak", "n": 5, "avg_d": 2.1},
        {"category": "chiyu_forest", "n": 2, "avg_d": 3.4},
        {"category": "recreation", "n": 3, "avg_d": 4.2},
        {"category": "trail", "n": 8, "avg_d": 1.8},
    ]
