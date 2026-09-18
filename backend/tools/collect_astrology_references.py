"""Fetch external evidence only; never import the production engine or pyswisseph.

Run explicitly with network access. Normal tests only read checked-in evidence.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import Request, urlopen

FIXTURES = Path(__file__).resolve().parents[1] / "tests/fixtures"
SOURCES = FIXTURES / "astrology_sources"


def fetch(name, url):
    SOURCES.mkdir(exist_ok=True)
    path = SOURCES / name
    if path.exists():
        return
    with urlopen(Request(url, headers={"User-Agent": "YasamKodu-ReferenceVerification/1.0"}), timeout=60) as response:
        data = response.read()
    provenance = {"url": url, "retrieved_at": datetime.now(timezone.utc).isoformat(),
                  "http_body_sha256": hashlib.sha256(data).hexdigest()}
    if name.startswith("swetest_"):
        pre = re.search(r"<pre[^>]*>(.*?)</pre>", data.decode("utf-8"), re.S | re.I)
        if pre is None:
            raise ValueError("Missing swetest output")
        data = (html.unescape(re.sub(r"<[^>]+>", "", pre.group(1))).strip() + "\n").encode("utf-8")
        provenance["extraction"] = "PRE text only; HTML formatting removed, numbers unchanged"
    path.write_bytes(data)
    provenance["sha256"] = hashlib.sha256(data).hexdigest()
    path.with_suffix(path.suffix + ".provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8")
    print(name, len(data), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=("horizons", "swetest", "all"), default="all")
    args = parser.parse_args()
    cases = json.loads((FIXTURES / "birth_cases.json").read_text(encoding="utf-8"))["cases"]
    if args.source in ("horizons", "all"):
        # Julian dates here are UTC labels, derived with stdlib, not the engine under test.
        dates = [datetime.fromisoformat(c["timezone"]["expected_utc"]) for c in cases]
        tlist = ",".join(f"{dt.timestamp() / 86400 + 2440587.5:.10f}" for dt in dates)
        for body, target in {"sun": "10", "moon": "301", "mercury": "199", "jupiter": "5"}.items():
            params = {"format": "json", "COMMAND": f"'{target}'", "EPHEM_TYPE": "'OBSERVER'",
                      "CENTER": "'500@399'", "TLIST": f"'{tlist}'", "TLIST_TYPE": "'JD'",
                      "TIME_TYPE": "'UT'", "QUANTITIES": "'31'", "REF_SYSTEM": "'ICRF'",
                      "APPARENT": "'AIRLESS'", "CSV_FORMAT": "'YES'", "EXTRA_PREC": "'YES'"}
            fetch(f"horizons_{body}.json", "https://ssd.jpl.nasa.gov/api/horizons.api?" + urlencode(params))
    if args.source in ("swetest", "all"):
        for case in cases:
            dt = datetime.fromisoformat(case["timezone"]["expected_utc"])
            loc = case["location"]
            command = (f"-b{dt.day}.{dt.month}.{dt.year} -utc{dt:%H:%M:%S} -p0123456789tA "
                       f"-house{loc['longitude']},{loc['latitude']},P -hsyP "
                       f"-geopos{loc['longitude']},{loc['latitude']},0 -fPlbsj -g, -n1 -emos")
            fetch(f"swetest_{case['id']}.txt", "https://www.astro.com/cgi/swetest.cgi?" + urlencode({"arg": command}))


if __name__ == "__main__":
    main()
