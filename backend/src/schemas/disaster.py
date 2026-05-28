"""
M10 — 산림재난 통합 알림 (v2 신설, 이상호 위원 강제).
Microclimate downscaling: 평지 → 산악 (풍속 3배, 강수 2배).
"""
from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, Field, confloat, conint


class MicroclimateForecast(BaseModel):
    """평지 기상 → 산악 기상 downscaling 단일 예보."""
    lat: float
    lon: float
    elevation_m: float
    forecast_time: datetime

    plain_temp_c: float
    plain_wind_ms: float
    plain_rain_mm: float

    # downscaling 결과
    mountain_temp_c: float
    mountain_wind_ms: float = Field(..., description="평지 wind × 3 (산악 경험적 계수)")
    mountain_rain_mm: float = Field(..., description="평지 rain × 2")

    # 출처
    source_komis_station_id: str | None = None
    source_kma_grid: str | None = None
    downscaling_model_version: str = "v1.0-empirical"
    r_squared: confloat(ge=0, le=1) = Field(0.7, description="downscaling 검증 R² (목표 ≥ 0.7)")


class DisasterAlert(BaseModel):
    """M10 일일 push 알림 한 건."""
    user_id: str
    lot_pnu: str
    alert_date: date
    risk_type: Literal["wildfire", "landslide", "frost", "drought"]
    risk_score: confloat(ge=0, le=1)
    risk_level: Literal["관심", "주의", "경계", "심각"]
    headline: str = Field(..., description="예: '산불 경계 — 임야 5km 반경 풍속 18m/s, 건조'")
    detail: str
    recommended_action: str = Field(
        default="이번 주 산림조합·산불감시원 협의 권장"
    )
    push_channel: Literal["kakao", "email", "both"] = "both"
    sent_at: datetime | None = None
