"""Read-only check of hand-selected expectations against pinned IANA rules.

No production service import and no fixture writes. UTC expectations were selected
by subtracting the seasonal UTC offset from the synthetic local calendar time.
"""
from datetime import datetime, timezone
from importlib.resources import files
import json
from pathlib import Path
from zoneinfo import ZoneInfo

import tzdata


def main():
    cases = json.loads((Path(__file__).resolve().parents[1] /
                        "tests/fixtures/birth_cases.json").read_text(encoding="utf-8"))["cases"]
    print(f"Independent fixture check: stdlib ZoneInfo / tzdata {tzdata.__version__}")
    for case in cases:
        expected = case["timezone"]
        with files("tzdata.zoneinfo").joinpath(*expected["iana"].split("/")).open("rb") as source:
            zone = ZoneInfo.from_file(source, key=expected["iana"])
        wall = datetime.fromisoformat(case["birth"]["local_date"] + "T" + case["birth"]["local_time"])
        local = wall.replace(tzinfo=zone)
        utc = local.astimezone(timezone.utc)
        assert utc == datetime.fromisoformat(expected["expected_utc"]), case["id"]
        assert local.utcoffset().total_seconds() / 60 == expected["expected_offset_minutes"], case["id"]
        assert bool(local.dst().total_seconds()) == expected["expected_dst"], case["id"]
        assert utc.astimezone(zone).replace(tzinfo=None) == wall, case["id"]
        assert wall.replace(tzinfo=zone, fold=1).utcoffset() == local.utcoffset(), case["id"]
        print(case["id"], expected["iana"], utc.isoformat(), expected["expected_offset_minutes"], expected["expected_dst"])
    print(f"{len(cases)} synthetic cases verified; no production output used.")


if __name__ == "__main__":
    main()
