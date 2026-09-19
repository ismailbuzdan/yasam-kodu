"""External swetest evidence for synthetic HD research; no production imports."""
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1] / "tests/fixtures"


def main():
    cases = json.loads((ROOT / "human_design_cases.json").read_text())["cases"]
    candidates = json.loads((ROOT / "human_design_sources/pyhd.json").read_text())["cases"]
    designs = {c["case_id"]: c["design_datetime"] for c in candidates}
    for case in cases:
        for side, stamp in (("personality", case["utc_datetime"]), ("design", designs[case["case_id"]])):
            dt = datetime.fromisoformat(stamp)
            command = f"-b{dt.day}.{dt.month}.{dt.year} -utc{dt:%H:%M:%S.%f} -p0123456789t -fPl -g, -n1 -emos"
            url = "https://www.astro.com/cgi/swetest.cgi?" + urlencode({"arg": command})
            with urlopen(Request(url, headers={"User-Agent": "YasamKodu-Research/1.0"}), timeout=30) as response:
                raw = response.read()
            match = re.search(r"<pre[^>]*>(.*?)</pre>", raw.decode(), re.S | re.I)
            if match is None:
                raise ValueError("No external swetest evidence")
            evidence = (html.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip() + "\n").encode()
            target = ROOT / f"human_design_sources/swetest_{case['case_id']}_{side}.txt"
            target.write_bytes(evidence)
            provenance = {"url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
                          "utc_datetime": stamp, "node_type": "true", "mode": "Moshier",
                          "independence": "external Swiss execution; shared algorithm, not JPL astronomy; design time supplied by PyHD",
                          "http_body_sha256": hashlib.sha256(raw).hexdigest(),
                          "sha256": hashlib.sha256(evidence).hexdigest(), "extraction": "PRE numeric output only"}
            target.with_suffix(".provenance.json").write_text(json.dumps(provenance, indent=2)+"\n")
            print(target.name, flush=True)


if __name__ == "__main__":
    main()
