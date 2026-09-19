"""Protect research provenance/acceptance boundaries, not production HD accuracy."""
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).parent / "fixtures"


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def test_synthetic_utc_case_contract():
    cases = load("human_design_cases.json")["cases"]
    assert len(cases) == 12
    assert len({c["case_id"] for c in cases}) == 12
    for case in cases:
        assert set(case) == {"case_id", "utc_datetime"}
        assert case["case_id"].startswith("hd_synthetic_")
        assert datetime.fromisoformat(case["utc_datetime"]).utcoffset() == timedelta(0)


def test_candidates_cannot_be_mistaken_for_approved_expectations():
    refs = load("human_design_references.json")
    assert refs["accepted_expectations"] == []
    assert refs["stage_9b_ready"] is False
    assert refs["stage_9a_complete"] is False
    ids = {c["case_id"] for c in load("human_design_cases.json")["cases"]}
    assert {c["case_id"] for c in refs["cases"]} == ids
    assert all(c["status"] == "candidate_not_approved" for c in refs["cases"])


def test_all_evidence_hashes_and_case_identity():
    refs = load("human_design_references.json")
    actual = {f"human_design_sources/{p.name}" for p in (ROOT / "human_design_sources").iterdir()}
    assert {a["path"] for a in refs["artifacts"]} == actual
    for artifact in refs["artifacts"]:
        assert hashlib.sha256((ROOT / artifact["path"]).read_bytes()).hexdigest() == artifact["sha256"]
    candidates = load("human_design_sources/pyhd.json")
    comparison = load("human_design_sources/comparison.json")
    assert comparison["astronomy_input_sha256"] == hashlib.sha256((ROOT / "human_design_sources/pyhd.json").read_bytes()).hexdigest()
    assert [c["case_id"] for c in candidates["cases"]] == [c["case_id"] for c in comparison["cases"]]
    for source in candidates["source_files"] + comparison["source_files"]:
        assert len(source["sha256"]) == 64
        assert datetime.fromisoformat(source["retrieved_at"].replace("Z", "+00:00")).tzinfo
        assert source["url"].startswith("https://raw.githubusercontent.com/")


def test_two_source_topology_integrity():
    a = load("human_design_sources/pyhd.json")["structural"]
    b = load("human_design_sources/comparison.json")["structural"]
    aliases = {"heart":"ego", "splenic":"spleen", "solarplexus":"solar_plexus"}
    normalize = lambda t: {int(k):aliases.get(v,v) for k,v in t.items()}
    assert normalize(a["gate_centers"]) == normalize(b["gate_centers"])
    assert set(normalize(a["gate_centers"])) == set(range(1,65))
    assert len(set(normalize(a["gate_centers"]).values())) == 9
    channels = {tuple(sorted(c)) for c in a["channels"]}
    assert channels == {tuple(sorted(c)) for c in b["channels"]}
    assert len(channels) == 36
    centers = normalize(a["gate_centers"])
    assert all(centers[x] != centers[y] for x,y in channels)


def test_disagreements_are_preserved_and_not_promoted():
    comparison = load("human_design_sources/comparison.json")
    anchor = next(r for r in comparison["boundaries"] if r["longitude"] == 302)
    assert anchor["free"] != anchor["wheel"]
    assert any(c["activation_disagreements"] for c in comparison["cases"])
    assert load("human_design_references.json")["limitations"]
