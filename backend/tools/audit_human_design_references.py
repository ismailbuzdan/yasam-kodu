"""Offline evidence inventory/comparison only, not a Human Design calculator."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "tests/fixtures"


def main():
    pyhd = json.loads((ROOT / "human_design_sources/pyhd.json").read_text())
    comparison = json.loads((ROOT / "human_design_sources/comparison.json").read_text())
    cases = json.loads((ROOT / "human_design_cases.json").read_text())["cases"]
    records = []
    max_delta = 0.0
    max_arc_residual = 0.0
    label = {"north_node": "true Node"}
    for case, chart in zip(cases, pyhd["cases"], strict=True):
        assert case["case_id"] == chart["case_id"]
        suns = {}
        for side in ("personality", "design"):
            evidence = ROOT / f"human_design_sources/swetest_{case['case_id']}_{side}.txt"
            raw = evidence.read_bytes()
            provenance = json.loads(evidence.with_suffix(".provenance.json").read_text())
            assert hashlib.sha256(raw).hexdigest() == provenance["sha256"]
            numbers = {m[0].strip(): float(m[1]) for m in re.findall(
                r"^([A-Za-z ]+),\s*([0-9.]+)\s*$", raw.decode(), re.M)}
            assert len(numbers) == 11
            suns[side] = numbers["Sun"]
            for activation in chart[side]:
                if activation["body"] in {"earth", "south_node"}:
                    continue
                expected = numbers[label.get(activation["body"], activation["body"].capitalize())]
                delta = abs((activation["longitude"] - expected + 180) % 360 - 180)
                max_delta = max(max_delta, delta)
        residual = abs((suns["personality"] - suns["design"] - 88 + 180) % 360 - 180)
        max_arc_residual = max(max_arc_residual, residual)
        records.append({"case_id":case["case_id"], "status":"candidate_not_approved",
                        "design_days_before_birth":(datetime.fromisoformat(case["utc_datetime"])
                          - datetime.fromisoformat(chart["design_datetime"])).total_seconds()/86400})
    aliases = {"heart":"ego", "splenic":"spleen", "solarplexus":"solar_plexus"}
    canonical = lambda table: {k:aliases.get(v,v) for k,v in table.items()}
    centers_match = canonical(pyhd["structural"]["gate_centers"]) == canonical(comparison["structural"]["gate_centers"])
    channels_match = sorted(pyhd["structural"]["channels"]) == sorted(comparison["structural"]["channels"])
    sources = []
    for file in sorted((ROOT / "human_design_sources").iterdir()):
        sources.append({"path":f"human_design_sources/{file.name}", "sha256":hashlib.sha256(file.read_bytes()).hexdigest()})
    differences = [d for c in comparison["cases"] for d in c["activation_disagreements"]]
    result = {"schema_version":1,"stage_9a_complete":False,"stage_9b_ready":False,
              "accepted_expectations":[], "cases":records, "artifacts":sources,
              "checks":{"gate_centers_match":centers_match,"channels_match":channels_match,
                "activation_count":len(cases)*26,
                "free_vs_pyhd_gate_line_disagreements":sum(d["free"]!=d["pyhd"] for d in differences),
                "wheel_vs_pyhd_gate_line_disagreements":sum(d["wheel"]!=d["pyhd"] for d in differences),
                "external_swetest_max_delta_degrees":max_delta,
                "external_swetest_max_88_degree_residual":max_arc_residual},
              }
    # Read-only audit: never replace recorded hashes with hashes of changed evidence.
    recorded = json.loads((ROOT / "human_design_references.json").read_text())
    assert len(recorded['artifacts']) == len(sources), 'Evidence inventory mismatch'
    assert {a['path']: a['sha256'] for a in recorded['artifacts']} == {
        a['path']: a['sha256'] for a in sources}, 'Evidence hash mismatch'
    for key in ('schema_version', 'stage_9a_complete', 'stage_9b_ready',
                'accepted_expectations', 'cases', 'checks'):
        assert recorded[key] == result[key], f'Recorded {key} mismatch'
    from inspect_human_design_official import build_report
    official = build_report()
    assert official == json.loads((ROOT / 'human_design_official_comparison.json').read_text())
    print(json.dumps(result["checks"],indent=2))
    print(json.dumps({'official_chart_count': len(official['cases']),
                      'evidence_files_verified': len(sources), 'audit_mode': 'read_only'}))


if __name__ == "__main__":
    main()
