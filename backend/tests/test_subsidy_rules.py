"""M06 subsidy_rules.yaml 정합성 검증."""
from pathlib import Path
import yaml

RULES = Path(__file__).parent.parent / "src" / "modules" / "m06_subsidy" / "subsidy_rules.yaml"


def test_loads():
    d = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    assert "subsidies" in d


def test_25_plus():
    d = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    assert len(d["subsidies"]) >= 25


def test_2026_new_3():
    d = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    codes = {s["code"] for s in d["subsidies"]}
    assert "SUB_MIRAE_CENTER" in codes
    assert "SUB_SHIMTER_SHELTER" in codes
    assert "SUB_YEONGYANG_SMARTFARM" in codes
    new = [s for s in d["subsidies"] if s.get("is_2026_new")]
    assert len(new) >= 3


def test_yeongyang_age_18_40():
    d = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    yy = next(s for s in d["subsidies"] if s["code"] == "SUB_YEONGYANG_SMARTFARM")
    assert yy["eligibility_age_min"] == 18
    assert yy["eligibility_age_max"] == 40
    assert "경상북도" in yy["eligibility_region"]


def test_critical_cite_law():
    d = yaml.safe_load(RULES.read_text(encoding="utf-8"))
    for code in ["SUB_DIRECT_PAY", "SUB_SHIMTER_SHELTER", "SUB_KOC_REGISTER"]:
        s = next(x for x in d["subsidies"] if x["code"] == code)
        assert s.get("cite_law"), f"{code} missing cite_law"
