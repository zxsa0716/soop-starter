"""
M05 — 5년 소득 시뮬레이션 (Prophet+LGBM + Bootstrap MC + 임가경제조사 calibrated).
"""
from typing import Optional
from pydantic import BaseModel, Field, confloat, conint


class FanChartPoint(BaseModel):
    """5년 fan chart 단일 연도 분위수."""
    year: conint(ge=0, le=10)
    p10_won: int
    p50_won: int
    p90_won: int
    cumulative_p10_won: int
    cumulative_p50_won: int
    cumulative_p90_won: int


class MonteCarloTrajectory(BaseModel):
    """단일 MC trajectory (1만 중 1개). 보통 반환 안 함, 디버깅용."""
    trajectory_id: conint(ge=0)
    annual_income_won: list[int] = Field(..., min_length=5, max_length=5)
    annual_cost_won: list[int]
    annual_subsidy_won: list[int]


class IncomeScenario(BaseModel):
    """
    M05 출력. 93,000 grid lookup의 한 cell.

    Grid 차원: 466 마을 × Top-10 임산물 × 5 자본 구간 × 4 면적 구간 = 93,000
    """
    village_admin_code: str
    product_code: str
    capital_bracket: str = Field(..., description="'2천만', '5천만', '1억', '1.5억', '3억+'")
    area_bracket: str = Field(..., description="'0.15ha', '0.3ha', '0.5ha', '1ha+'")

    # 5년 fan chart
    annual_points: list[FanChartPoint] = Field(..., min_length=5, max_length=5)

    # 5년 누적
    cumulative_5y_p10_won: int
    cumulative_5y_p50_won: int
    cumulative_5y_p90_won: int

    # Calibration 정보 (학술 정직성 — 김재현 위원 요구)
    n_trajectories: conint(ge=1000) = 10000
    calibration_prior: str = Field(
        default="임가경제조사 1,500가구 8업종 Bootstrap",
        description="이론적 가우시안 대신 실측 prior — 학술 contribution",
    )
    calibration_error_pct: Optional[confloat(ge=0, le=100)] = Field(
        None, description="임가경제 median 대비 오차 (목표 ≤ 12%)"
    )

    # 비교선
    nong_eo_chon_median_p50_won: Optional[int] = Field(
        None, description="임가경제조사 동일 업종 median (overlay 비교선)"
    )

    # 출처
    source_models: list[str] = Field(
        default_factory=lambda: ["Prophet+LGBM stacking", "Bootstrap MC", "표준품셈 2021"]
    )
