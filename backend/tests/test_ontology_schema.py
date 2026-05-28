"""ForKG-Korea + function schemas 검증."""
import json
from pathlib import Path
import yaml

ROOT = Path(__file__).parent.parent.parent
ONTO = ROOT / "data" / "ontology" / "forkg_korea_ontology.yaml"
SCHEMAS = ROOT / "backend" / "src" / "agent" / "function_schemas.json"
PROMPT = ROOT / "backend" / "src" / "agent" / "system_prompt.md"


def test_ontology_9_11():
    d = yaml.safe_load(ONTO.read_text(encoding="utf-8"))
    assert len(d["entities"]) >= 9
    assert len(d["relations"]) >= 11


def test_forpkg_cited():
    d = yaml.safe_load(ONTO.read_text(encoding="utf-8"))
    assert d["meta"]["upstream_framework"] == "ForPKG-1.0"
    assert "arXiv" in d["meta"]["upstream_citation"]


def test_11_tools():
    d = json.loads(SCHEMAS.read_text(encoding="utf-8"))
    assert len(d["tools"]) == 11


def test_tool_names_match_modules():
    d = json.loads(SCHEMAS.read_text(encoding="utf-8"))
    expected = {"extract_user_profile", "filter_candidate_villages",
                "recommend_forest_products", "find_similar_villages",
                "simulate_5year_income", "match_subsidies_timeline",
                "assess_shimter_eligibility", "answer_with_rag",
                "find_mentors_and_cooperatives", "register_disaster_alert",
                "score_lifestyle_axes"}
    assert {t["name"] for t in d["tools"]} == expected


def test_prompt_has_5_states():
    txt = PROMPT.read_text(encoding="utf-8")
    for s in ["Profiling", "Narrowing", "Matching", "Decision", "Free Q&A"]:
        assert s in txt or s.lower() in txt.lower()


def test_citation_guardrail():
    txt = PROMPT.read_text(encoding="utf-8")
    assert "인용" in txt
    assert "거절" in txt or "guardrail" in txt.lower()
