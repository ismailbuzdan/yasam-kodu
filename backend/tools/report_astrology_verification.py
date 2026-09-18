"""Compare production outputs to immutable external evidence; never write fixtures."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.schemas.astrology import AstrologyRequest
from app.services.astrology_service import AstrologyService, angular_distance


def main():
    root = Path(__file__).resolve().parents[1] / "tests/fixtures"
    cases = {c["id"]:c for c in json.loads((root / "birth_cases.json").read_text(encoding="utf-8"))["cases"]}
    references = json.loads((root / "astrology_references.json").read_text())["reference_records"]
    print("case | Sun arcsec | Moon arcsec | Mercury arcsec | Jupiter arcsec | ASC arcsec | MC arcsec | Max cusp arcsec | Sun/Moon/ASC signs")
    for ref in references:
        c = cases[ref["case_id"]]
        result = AstrologyService().calculate(AstrologyRequest(utc_datetime=c["timezone"]["expected_utc"],
                    latitude=c["location"]["latitude"],longitude=c["location"]["longitude"]))
        exp = ref["expected"]
        differences = [angular_distance(result.bodies[b].longitude, exp["planet_longitudes"][b]) * 3600 for b in ("sun","moon","mercury","jupiter")]
        differences += [angular_distance(result.ascendant.longitude, exp["ascendant_longitude"]) * 3600,
                        angular_distance(result.mc.longitude, exp["mc_longitude"]) * 3600,
                        max(angular_distance(h.longitude, cusp) for h,cusp in zip(result.houses,exp["house_cusps"])) * 3600]
        signs = (result.bodies["sun"].sign,result.bodies["moon"].sign,result.ascendant.sign)
        print(ref["case_id"] + " | " + " | ".join(f"{d:.6f}" for d in differences) + " | " + "/".join(signs))


if __name__ == "__main__":
    main()
