"""4 페르소나 E2E 검증 (fixture-only mode)."""
from __future__ import annotations
import json
from pathlib import Path
import pytest

FIXTURES = Path(__file__).parent.parent.parent / "data" / "fixtures"


@pytest.fixture(params=["p01", "p02", "p03", "p04"])
def persona(request):
    fp = FIXTURES / f"persona_{request.param}.json"
    return json.loads(fp.read_text(encoding="utf-8"))


def test_has_required_fields(persona):
    for k in ["persona_id", "name", "age", "scenario_summary", "hit_policy_2026",
              "demo_time_seconds", "module_results", "final_summary"]:
        assert k in persona


def test_demo_under_15s(persona):
    assert persona["demo_time_seconds"] <= 15


def test_user_profile_completeness(persona):
    up = persona["module_results"]["extract_user_profile"]
    assert up.get("completeness_score", 0) >= 0.6


def test_filter_at_least_1_candidate(persona):
    f = persona["module_results"]["filter_candidate_villages"]
    assert f["n_in"] == 466
    assert f["n_out"] >= 1


def test_recommendation_has_shap(persona):
    rec = persona["module_results"]["recommend_forest_products"]["recommendations"]
    assert len(rec) >= 1
    top = rec[0]
    assert "typical_5yr_revenue" in top


def test_income_p50_matches(persona):
    sim = persona["module_results"]["simulate_5year_income"]
    expected = {"P-01": 119_000_000, "P-02": 45_000_000, "P-03": 180_000_000, "P-04": 270_000_000}
    assert abs(sim["cumulative_5y_p50_won"] - expected[persona["persona_id"]]) <= 5_000_000


def test_subsidy_has_this_week(persona):
    m = persona["module_results"]["match_subsidies_timeline"]
    assert m["this_week_top_action"]["is_this_week_action"] is True


def test_p01_shimter_eligible():
    d = json.load(open(FIXTURES / "persona_p01.json"))
    assert d["module_results"]["assess_shimter_eligibility"]["is_eligible"] is True


def test_p04_yeongyang_smartfarm():
    d = json.load(open(FIXTURES / "persona_p04.json"))
    up = d["module_results"]["extract_user_profile"]
    assert up["age"] == 30 and up["eligible_for_young_subsidy"] is True


def test_p03_inherited_lot():
    d = json.load(open(FIXTURES / "persona_p03.json"))
    assert d["module_results"]["extract_user_profile"]["inherited_lot_area_ha"] == 3.0


def test_p02_shimter_not_eligible_alt():
    d = json.load(open(FIXTURES / "persona_p02.json"))
    sh = d["module_results"]["assess_shimter_eligibility"]
    assert sh["is_eligible"] is False
