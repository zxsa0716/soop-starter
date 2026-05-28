"""
M01 사용자 프로파일링 에이전트
==============================
3턴 max + 자연어/슬라이더 hybrid (박지영 위원 강제 사항).
27 결정 변수 추출.

호출 흐름:
  Turn 1: 자유 자연어 → Claude로 18~22 fields 추출
  Turn 2: 카드+슬라이더로 사용자 검토·수정
  Turn 3: 누락 1~2 필드만 직접 질문
"""
from .agent import extract_user_profile

__all__ = ["extract_user_profile"]
