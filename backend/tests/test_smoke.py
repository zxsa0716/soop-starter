"""Smoke tests — 모든 schema import 가능 + 4 페르소나 fixture 로드 가능."""
from __future__ import annotations
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent


def test_schemas_importable():
    from src import schemas  # noqa
    from src.schemas import UserProfile, Village, ForestProductRecommendation, IncomeScenario
    assert UserProfile and Village and ForestProductRecommendation and IncomeScenario


def test_function_schemas_json_valid():
    p = REPO_ROOT / "backend" / "src" / "agent" / "function_schemas.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert len(data["tools"]) == 11
    names = {t["name"] for t in data["tools"]}
    expected = {
        "extract_user_profile", "filter_candidate_villages", "recommend_forest_products",
        "find_similar_villages", "simulate_5year_income", "match_subsidies_timeline",
        "assess_shimter_eligibility", "answer_with_rag", "find_mentors_and_cooperatives",
        "register_disaster_alert", "score_lifestyle_axes",
    }
    assert names == expected, f"missing: {expected - names}"


@pytest.mark.parametrize("persona_id", ["p01", "p02", "p03", "p04"])
def test_persona_fixture_loadable(persona_id: str):
    p = REPO_ROOT / "data" / "fixtures" / f"persona_{persona_id}.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["persona_id"].lower().endswith(persona_id[-2:])
    assert "module_results" in data
    assert "extract_user_profile" in data["module_results"]


def test_forkg_ontology_shape():
    import yaml
    p = REPO_ROOT / "data" / "ontology" / "forkg_korea_ontology.yaml"
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    assert len(data["entities"]) >= 9
    assert len(data["relations"]) >= 11
    assert data["meta"]["upstream_framework"] == "ForPKG-1.0"


def test_user_profile_27_fields():
    from src.schemas import UserProfile
    fields = set(UserProfile.model_fields.keys()) - {"interview_turns", "completeness_score"}
    assert len(fields) >= 25, f"UserProfile must have ≥25 decision fields (got {len(fields)})"


def test_system_prompt_exists():
    p = REPO_ROOT / "backend" / "src" / "agent" / "system_prompt.md"
    txt = p.read_text(encoding="utf-8")
    assert "Claude Opus 4.7" in txt
    assert "11 모듈" in txt
    assert "REFUSE" in txt or "거절" in txt  # citation guardrail
