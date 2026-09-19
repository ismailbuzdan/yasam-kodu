"""Protect research provenance/acceptance boundaries, not production HD accuracy."""
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

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


def test_official_chart_provenance_and_complete_numeric_capture():
    paths = sorted((ROOT / 'human_design_sources').glob('jovian_*.json'))
    assert len(paths) == 14
    for path in paths:
        chart = json.loads(path.read_text())
        dt = datetime.fromisoformat(chart['utc_datetime'])
        assert dt.utcoffset() == timedelta(0)
        assert chart['status'] == 'candidate_not_approved'
        assert chart['source_url'] == 'https://jovianarchive.com/pages/get-your-human-design-chart'
        assert datetime.fromisoformat(chart['retrieved_at'].replace('Z', '+00:00')).tzinfo
        assert chart['version'] is None and chart['settings']['node_algorithm'] is None
        displayed = datetime.strptime(chart['raw']['properties']['Date and Time (UTC)'], '%B %d, %Y, %H:%M')
        assert displayed == dt.replace(tzinfo=None)
        for side in ('design', 'personality'):
            text = chart['raw'][side + '_text']
            assert len(text) == 14 and text[0].lower() == side
            for value in text[1:]:
                assert re.fullmatch(r'\d{1,2}\. [1-6]', value)
                assert 1 <= int(value.split('.')[0]) <= 64


def test_official_comparison_nodes_and_rare_coverage_are_observations():
    report = load('human_design_official_comparison.json')
    raw_path = ROOT / 'human_design_sources/pyhd_official_comparison_nodes.json'
    assert report['input_sha256'] == hashlib.sha256(raw_path.read_bytes()).hexdigest()
    raw = json.loads(raw_path.read_text())
    official = {c['case_id']: (p, c) for p in (ROOT / 'human_design_sources').glob('jovian_*.json')
                if (c := json.loads(p.read_text()))}
    assert len(raw['cases']) == len(report['cases']) == 14
    nodes = [n for c in raw['cases'] for n in c['nodes']]
    assert len(nodes) == 56
    assert sum(n['true']['gate_line'] == n['official'] for n in nodes) == 56
    assert sum(n['mean']['gate_line'] != n['official'] for n in nodes) == 46
    for c in raw['cases']:
        path, chart = official[c['case_id']]
        assert c['official_sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
        assert len(c['activations']) == 26
        assert all(a['pyhd'] == a['official'] for a in c['activations'])
        for side in ('personality', 'design'):
            pair = {n['body']: n for n in c['nodes'] if n['side'] == side}
            for algorithm in ('true', 'mean'):
                delta = (pair['south_node'][algorithm]['longitude'] - pair['north_node'][algorithm]['longitude']) % 360
                assert abs(delta - 180) < 1e-10
    props = [c['official'] for c in report['cases']]
    assert {p['Type'] for p in props} == {'Generator', 'Manifesting Generator', 'Manifestor', 'Projector', 'Reflector'}
    assert {'Ego Manifested', 'Ego Projected', 'Self Projected', 'Sounding Board', 'Lunar Cycle'} <= {p['Authority'] for p in props}
    assert {p['Definition'] for p in props} == {'None', 'Single', 'Split', 'Triple Split', 'Quadruple Split'}
    assert {'2/5', '3/6', '4/1', '5/2'} <= {p['Profile'] for p in props}
    assert report['status'] == raw['status'] == 'candidate_not_approved'


def test_audit_is_read_only_and_comparison_is_reproducible():
    files = list(ROOT.glob('human_design*.json')) + list((ROOT / 'human_design_sources').iterdir())
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in files if p.is_file()}
    result = subprocess.run([sys.executable, 'tools/audit_human_design_references.py'],
                            cwd=ROOT.parents[1], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'read_only' in result.stdout
    assert all(hashlib.sha256(p.read_bytes()).hexdigest() == digest for p, digest in before.items())
