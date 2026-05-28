"""
M07 산촌체류형 쉼터 입지 평가
==============================
산지관리법 시행령 일부개정안 7개 룰 + 표준품셈 6항목 비용 시뮬 (±15%).
법제처 OpenAPI 주 1회 sync.
"""
from .assessor import assess_shimter_eligibility

__all__ = ["assess_shimter_eligibility"]
