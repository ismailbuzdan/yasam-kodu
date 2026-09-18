"""Parse fetched external numerical evidence. No production/swiss imports allowed."""
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import re

FIXTURES = Path(__file__).resolve().parents[1] / "tests/fixtures"
SOURCES = FIXTURES / "astrology_sources"
NAMES = {"Sun":"sun", "Moon":"moon", "Mercury":"mercury", "Venus":"venus",
         "Mars":"mars", "Jupiter":"jupiter", "Saturn":"saturn", "Uranus":"uranus",
         "Neptune":"neptune", "Pluto":"pluto", "true Node":"true_north_node", "mean Apogee":"lilith"}


def load_evidence():
    horizons = {}
    for body in ("sun", "moon", "mercury", "jupiter"):
        data = json.loads((SOURCES / f"horizons_{body}.json").read_text())
        result = data["result"]
        assert "GEOCENTRIC" in result and "AIRLESS" in result and "DE441" in result
        rows = csv.reader(result.split("$$SOE")[1].split("$$EOE")[0].strip().splitlines())
        horizons[body] = {
            datetime.strptime(row[0].strip(), "%Y-%b-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc):
            {"longitude": float(row[3]), "latitude": float(row[4])} for row in rows}
    return horizons


def parse_swetest(case_id):
    text = (SOURCES / f"swetest_{case_id}.txt").read_text()
    assert "version 2.10.03" in text and "Houses system P (Placidus)" in text
    assert "-utc" in text and "-emos" in text
    bodies, cusps, angles = {}, [], {}
    for row in csv.reader(text.splitlines()):
        if len(row) < 2:
            continue
        name = row[0].strip()
        if name in NAMES:
            bodies[NAMES[name]] = {"longitude":float(row[1]), "latitude":float(row[2]),
                                   "speed_longitude":float(row[3]), "house_position":float(row[4]),
                                   "house":int(float(row[4]))}
        elif re.fullmatch(r"house\s+\d+", name):
            cusps.append(float(row[1]))
        elif name in ("Ascendant", "MC"):
            angles[name] = float(row[1])
    assert len(cusps) == 12 and len(bodies) == 12 and len(angles) == 2
    return bodies, cusps, angles


def build():
    cases = json.loads((FIXTURES / "birth_cases.json").read_text(encoding="utf-8"))["cases"]
    reference = json.loads((FIXTURES / "astrology_references.json").read_text())
    horizons = load_evidence()
    records = []
    for case in cases:
        dt = datetime.fromisoformat(case["timezone"]["expected_utc"])
        bodies, cusps, angles = parse_swetest(case["id"])
        source_files = [f"horizons_{body}.json" for body in horizons] + [f"swetest_{case['id']}.txt"]
        provenance = []
        for name in source_files:
            p = json.loads((SOURCES / (name + ".provenance.json")).read_text())
            provenance.append({"artifact": "astrology_sources/" + name, **p})
        records.append({
            "case_id":case["id"],
            "reference_source":{
                "name":"NASA/JPL Horizons + Astrodienst public swetest",
                "version":"Horizons API 1.2 / DE441; swetest 2.10.03 Moshier",
                "retrieved_at":provenance[0]["retrieved_at"], "artifacts":provenance,
                "notes":"Planet expectations: external JPL DE441, apparent geocentric IAU76/80 ecliptic-of-date (quantity 31), airless, UTC. Angles/cusps/body placement: externally executed swetest Tropical/Placidus, UTC input, Moshier; shared Swiss library, NOT independent algorithm. Modern-model differences against IAU76/80 included in 0.01-degree budget; no geometric/J2000/topocentric mixing.",
                "field_sources":{"sun_longitude":"horizons_sun", "moon_longitude":"horizons_moon",
                                 "planet_longitudes":"horizons", "ascendant_longitude":"swetest",
                                 "mc_longitude":"swetest", "house_cusps":"swetest", "swetest_bodies":"swetest"}},
            "conventions":{"zodiac":"tropical", "house_system":"placidus", "node_type":"true",
                           "lilith_type":"mean_black_moon", "time_scale":"UTC", "observer":"geocentric"},
            "expected":{"sun_longitude":horizons["sun"][dt]["longitude"],
                        "moon_longitude":horizons["moon"][dt]["longitude"],
                        "ascendant_longitude":angles["Ascendant"], "mc_longitude":angles["MC"],
                        "planet_longitudes":{name:values[dt]["longitude"] for name,values in horizons.items()},
                        "planet_latitudes":{name:values[dt]["latitude"] for name,values in horizons.items()},
                        "house_cusps":cusps, "swetest_bodies":bodies},
            "tolerance":{"planet_degrees":0.01,"angles_degrees":0.05,
                         "swetest_planet_degrees":0.00001, "speed_degrees_per_day":0.00001}})
    reference["reference_records"] = records
    (FIXTURES / "astrology_references.json").write_text(json.dumps(reference,indent=2)+"\n",encoding="utf-8")
    print(f"Built {len(records)} externally sourced records; template preserved.")


if __name__ == "__main__":
    build()
