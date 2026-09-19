"""Research-only external-engine adapter. Never imports app or implements HD rules.

Run explicitly in the backend Docker container. Downloads pinned MIT PyHD into a
temporary directory, not into the project/dependencies. Stores only mechanical
output and provenance, never upstream interpretation text or source code.
Candidates are NOT approved expectations for a future production engine.
"""
from datetime import datetime, timezone
from enum import Enum
import hashlib
import importlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen

FIXTURES = Path(__file__).resolve().parents[1] / "tests/fixtures"
COMMIT = "d80aef667e561fb588dd883f8ce39ceea9593a12"
BASE = f"https://raw.githubusercontent.com/ppo/pyhd/{COMMIT}/"
FILES = ["LICENSE", "pyproject.toml"] + ["src/pyhd/" + f for f in (
    "__init__.py", "activation.py", "chart.py", "imprint.py", "models.py",
    "constants/__init__.py", "constants/superenum.py", "utils/__init__.py",
    "utils/astro.py", "utils/data.py", "utils/debug.py", "utils/display.py",
    "utils/swissephemeris.py")]


def main():
    cases = json.loads((FIXTURES / "human_design_cases.json").read_text())["cases"]
    provenance = []
    with TemporaryDirectory(prefix="yasam-hd-reference-") as directory:
        root = Path(directory)
        for filename in FILES:
            url = BASE + filename
            with urlopen(Request(url, headers={"User-Agent": "YasamKodu-Research/1.0"}), timeout=30) as response:
                data = response.read()
            path = root / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            provenance.append({"url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
                               "sha256": hashlib.sha256(data).hexdigest()})
        if not (root / "LICENSE").read_text().startswith("MIT License"):
            raise ValueError("Unexpected external license; do not execute")
        sys.path.insert(0, str(root / "src"))
        # Upstream advertises >=3.10 but uses the Python 3.13 Enum alias API.
        # Research-only compatibility adapter; no calculation functions changed.
        # The deviation is recorded and prevents promotion to approved goldens.
        if not hasattr(Enum, "_add_value_alias_"):
            def add_alias(member, value):
                mapping = member.__class__._value2member_map_
                if value in mapping and mapping[value] is not member:
                    raise ValueError("Conflicting enum alias")
                mapping[value] = member
            Enum._add_value_alias_ = add_alias
        pyhd = importlib.import_module("pyhd")
        constants = importlib.import_module("pyhd.constants")
        import swisseph as swe
        # Isolate optional ephemeris/time files; retain upstream Moshier flags.
        swe.set_ephe_path(directory)
        results = []
        for case in cases:
            chart = pyhd.Chart(datetime.fromisoformat(case["utc_datetime"]))
            row = {"case_id": case["case_id"], "design_datetime": chart.design.dt.isoformat(),
                   "type": str(chart.type), "strategy": str(chart.strategy),
                   "authority": str(chart.authority), "profile": str(chart.profile),
                   "definition_components": len(chart.definitions),
                   "active_gates": sorted(int(g.num) for g in chart.gates),
                   "defined_centers": sorted(c._key.lower() for c in chart.centers),
                   "defined_channels": sorted([sorted(int(g.num) for g in c.gates) for c in chart.channels])}
            for side in ("personality", "design"):
                imprint = getattr(chart, side)
                row[side] = [{"body": body._key.lower(), "longitude": imprint[body].longitude,
                              "gate": int(imprint[body].gate.num), "line": int(imprint[body].line.num)}
                             for body in constants.Planets]
            results.append(row)
        structural = {
            "gate_centers": {str(g.num): g.center._key.lower() for g in constants.Gates},
            "channels": sorted([sorted(int(g.num) for g in c.gates) for c in constants.Channels]),
        }
        payload = {"status": "candidate_not_approved", "source": "ppo/pyhd", "commit": COMMIT,
                   "version": pyhd.__version__, "license": "MIT", "node_type": "true",
                   "adapter": "Python 3.11 Enum value-alias compatibility shim; upstream calculation source unmodified",
                   "ephemeris": f"Swiss {swe.version}; Moshier; shared algorithm, not independent astronomy",
                   "input": "synthetic UTC only", "source_files": provenance,
                   "structural": structural, "cases": results}
        target = FIXTURES / "human_design_sources/pyhd.json"
        target.parent.mkdir(exist_ok=True)
        target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Collected {len(results)} candidate cases from external PyHD")


if __name__ == "__main__":
    main()
