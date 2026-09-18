"""Compare Stage 6 projection with native house_pos. Diagnostic, not a reference generator."""
from datetime import datetime
import json
from pathlib import Path

import swisseph as swe


def main():
    cases = json.loads((Path(__file__).resolve().parents[1] / "tests/fixtures/birth_cases.json").read_text(encoding="utf-8"))["cases"]
    swe.set_ephe_path(None)
    differences = []
    for case in cases:
        dt = datetime.fromisoformat(case["timezone"]["expected_utc"])
        tt, ut = swe.utc_to_jd(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
        lat, lon = case["location"]["latitude"], case["location"]["longitude"]
        cusps, angles = swe.houses_ex(ut, lat, lon, b"P")
        eps = swe.calc(tt, swe.ECL_NUT, swe.FLG_MOSEPH)[0][0]
        for name, body in {"sun":0,"moon":1,"mercury":2,"venus":3,"mars":4,"jupiter":5,
                           "saturn":6,"uranus":7,"neptune":8,"pluto":9,"true_north_node":11,
                           "lilith":12,"south_node":11}.items():
            values, _ = swe.calc(tt, body, swe.FLG_MOSEPH | swe.FLG_SPEED)
            if name == "south_node":
                values = ((values[0] + 180) % 360, 0.0, *values[2:])
            projected = next(i + 1 for i, start in enumerate(cusps)
                             if (values[0] - start) % 360 < (cusps[(i + 1) % 12] - start) % 360)
            native = swe.house_pos(angles[2], lat, eps, values[:2], b"P")
            if projected != int(native):
                differences.append({"case_id":case["id"], "body":name,
                                    "interval_house":projected, "house_pos_house":int(native),
                                    "house_pos":native, "latitude":values[1]})
    print(json.dumps({"cases":len(cases), "bodies_per_case":13, "differences":differences}, indent=2))


if __name__ == "__main__":
    main()
