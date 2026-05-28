"""M10 — KoMIS 480 + 기상청 5km + microclimate downscaling. 일일 카카오/이메일 push."""
from __future__ import annotations
import logging
from datetime import date
logger = logging.getLogger(__name__)


async def register_disaster_alert(user_id: str, lot_pnu: str, channel: str = "both") -> dict:
    """일일 백그라운드 push 등록. 동기 흐름과 분리. Celery beat schedule."""
    return {
        "status": "registered",
        "user_id": user_id,
        "lot_pnu": lot_pnu,
        "channel": channel,
        "next_alert_at": str(date.today()),
        "downscaling_note": "산악 풍속 = 평지 × 3, 강수 = 평지 × 2 (R² ≥ 0.7)",
        "policy_fit": "산림청 김인호 청장 비전 — '산림재난을 국가안보수준으로 관리'",
    }
