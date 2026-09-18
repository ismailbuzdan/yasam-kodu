"""Deterministic geocentric tropical calculations; no location/timezone lookup."""
from importlib.metadata import version
from itertools import combinations
from math import isfinite
from os import environ
from tempfile import TemporaryDirectory
from threading import RLock

import swisseph as swe

from app.schemas.astrology import (
    Aspect, AstrologyMetadata, AstrologyRequest, AstrologyResponse,
    BodyPosition, HouseCusp, Position,
)

SIGNS = ("aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra",
         "scorpio", "sagittarius", "capricorn", "aquarius", "pisces")
BODIES = {"sun": swe.SUN, "moon": swe.MOON, "mercury": swe.MERCURY,
          "venus": swe.VENUS, "mars": swe.MARS, "jupiter": swe.JUPITER,
          "saturn": swe.SATURN, "uranus": swe.URANUS, "neptune": swe.NEPTUNE,
          "pluto": swe.PLUTO, "true_north_node": swe.TRUE_NODE, "lilith": swe.MEAN_APOG}
ASPECT_ANGLES = {"conjunction": 0, "sextile": 60, "square": 90,
                 "trine": 120, "opposition": 180}
ORB_POLICY = {"luminary": 8.0, "other": 6.0, "sextile": 4.0}
FLAGS = swe.FLG_MOSEPH | swe.FLG_SPEED
_LOCK = RLock()
_EPHEMERIS_DIRECTORY = TemporaryDirectory(prefix="yasam-kodu-moshier-")


class AstrologyError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def initialize_ephemeris() -> None:
    """Called under _LOCK on every worker thread, before any native calculation.

    A private empty directory prevents optional local time-model files from being
    loaded. The native API lets SE_EPHE_PATH override its argument, so reject it.
    """
    if environ.get("SE_EPHE_PATH"):
        raise AstrologyError("ephemeris_error", "Moshier için harici ephemeris yolu desteklenmiyor.")
    swe.set_ephe_path(_EPHEMERIS_DIRECTORY.name)
    swe.set_tid_acc(swe.TIDAL_AUTOMATIC)
    swe.set_delta_t_userdef(swe.DELTAT_AUTOMATIC)


def normalize_longitude(value: float) -> float:
    if not isfinite(value):
        raise AstrologyError("ephemeris_error", "Geçersiz hesap sonucu.")
    normalized = value % 360
    # Floating-point rounding of a tiny negative value can produce exactly 360.
    return 0.0 if normalized == 360 else normalized


def position(value: float) -> Position:
    longitude = normalize_longitude(value)
    return Position(longitude=longitude, sign=SIGNS[int(longitude // 30)],
                    degree_in_sign=longitude % 30)


def is_retrograde(speed: float) -> bool:
    return speed < 0


def angular_distance(first: float, second: float) -> float:
    distance = normalize_longitude(first - second)
    return min(distance, 360 - distance)


def house_for(longitude: float, cusps: tuple[float, ...]) -> int:
    """Legacy projected placement, retained only for audit/contrast tests."""
    # Each cusp belongs to the house beginning there; intervals are [start, end).
    for index, start in enumerate(cusps):
        end = cusps[(index + 1) % 12]
        if normalize_longitude(longitude - start) < normalize_longitude(end - start):
            return index + 1
    raise AstrologyError("house_calculation_error", "Ev yerleşimi hesaplanamadı.")


def placidus_house(longitude: float, latitude: float, armc: float, geolat: float,
                   obliquity: float, cusps: tuple[float, ...]) -> int:
    try:
        value = swe.house_pos(armc, geolat, obliquity, (longitude, latitude), b"P")
    except swe.Error as error:
        raise AstrologyError("house_calculation_error", "Ev yerleşimi hesaplanamadı.") from error
    if not isfinite(value) or not 1 <= value < 13:
        raise AstrologyError("house_calculation_error", "Geçersiz ev yerleşimi.")
    # Only zero-latitude points lie on an ecliptic cusp. Allow tiny roundoff.
    if latitude == 0:
        for index, cusp in enumerate(cusps):
            if angular_distance(longitude, cusp) <= 1e-10:
                return index + 1
    return int(value)


def aspects_for(bodies: dict[str, BodyPosition]) -> list[Aspect]:
    aspects = []
    for (name1, body1), (name2, body2) in combinations(bodies.items(), 2):
        separation = angular_distance(body1.longitude, body2.longitude)
        for kind, angle in ASPECT_ANGLES.items():
            limit = ORB_POLICY["sextile"] if kind == "sextile" else ORB_POLICY[
                "luminary" if {name1, name2} & {"sun", "moon"} else "other"]
            orb = abs(separation - angle)
            if orb <= limit:
                aspects.append(Aspect(body1=name1, body2=name2, type=kind,
                                      exact_angle=angle, separation=separation, orb=orb))
    return aspects


class AstrologyService:
    def calculate(self, request: AstrologyRequest) -> AstrologyResponse:
        # Serialize the native library's stateful calls. All flags are explicit.
        with _LOCK:
            return self._calculate(request)

    def _calculate(self, request: AstrologyRequest) -> AstrologyResponse:
        dt = request.utc_datetime
        try:
            initialize_ephemeris()
            # utc_to_jd returns (TT, UT1); houses require UT1 and planets use TT.
            jd_tt, jd_ut = swe.utc_to_jd(dt.year, dt.month, dt.day, dt.hour,
                                       dt.minute, dt.second + dt.microsecond / 1e6, swe.GREG_CAL)
            obliquity = swe.calc(jd_tt, swe.ECL_NUT, swe.FLG_MOSEPH)[0][0]
        except swe.Error as error:
            raise AstrologyError("ephemeris_error", "Ephemeris zamanı hesaplanamadı.") from error
        try:
            cusps, angles = swe.houses_ex(jd_ut, request.latitude, request.longitude, b"P", 0)
        except swe.Error as error:
            # Native Placidus failures must not expose its Porphyry fallback.
            raise AstrologyError("house_calculation_error", "Bu konum için Placidus evleri hesaplanamadı.") from error
        bodies = {}
        try:
            for name, body_id in BODIES.items():
                values, returned_flags = swe.calc(jd_tt, body_id, FLAGS)
                if not returned_flags & swe.FLG_MOSEPH or not returned_flags & swe.FLG_SPEED:
                    raise AstrologyError("ephemeris_error", "Beklenmeyen ephemeris hesap modu.")
                if not isfinite(values[3]):
                    raise AstrologyError("ephemeris_error", "Geçersiz hız hesap sonucu.")
                bodies[name] = BodyPosition(**position(values[0]).model_dump(),
                    speed_longitude=values[3], retrograde=is_retrograde(values[3]),
                    house=placidus_house(values[0], values[1], angles[2], request.latitude,
                                         obliquity, cusps))
        except swe.Error as error:
            raise AstrologyError("ephemeris_error", "Gök cismi konumları hesaplanamadı.") from error
        north = bodies["true_north_node"]
        south = position(north.longitude + 180)
        bodies["south_node"] = BodyPosition(**south.model_dump(),
            speed_longitude=north.speed_longitude, retrograde=north.retrograde,
            house=placidus_house(south.longitude, 0.0, angles[2], request.latitude, obliquity, cusps))
        return AstrologyResponse(
            metadata=AstrologyMetadata(pyswisseph_version=version("pyswisseph"),
                                       swiss_ephemeris_version=swe.version),
            bodies=bodies, ascendant=position(angles[0]), mc=position(angles[1]),
            houses=[HouseCusp(house=i + 1, **position(cusp).model_dump())
                    for i, cusp in enumerate(cusps)], aspects=aspects_for(bodies))
