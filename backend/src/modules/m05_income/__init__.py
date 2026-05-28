"""
M05 5년 소득 시뮬레이션
=======================
Prophet + LGBM stacking (가격) + Bootstrap Monte Carlo (소득) + 임가경제 1,500가구 8업종 calibrated.

★ 시연 안정성 backbone: 466 × Top-10 × 5 자본 × 4 면적 = 93,000 시나리오
   사전 계산 → DuckDB 정적 저장 → 1초 lookup.
"""
from .simulator import simulate_5year_income

__all__ = ["simulate_5year_income"]
