from datetime import date, datetime, time, timezone
from functools import lru_cache
from importlib.resources import files
from math import isfinite
from threading import Lock
from zoneinfo import ZoneInfo

from timezonefinder import TimezoneFinder

from app.schemas.timezone import TimezoneCandidate, TimezoneResponse


class TimezoneError(Exception):
    def __init__(self, code: str, message: str, *, zone: str | None = None,
                 candidates: list[TimezoneCandidate] | None = None):
        super().__init__(message)
        self.code = code
        self.zone = zone
        self.candidates = candidates or []


@lru_cache(maxsize=256)
def load_zone(name: str) -> ZoneInfo:
    # Always use the pinned package, including on hosts with different system tzdb.
    if any(part in ("", ".", "..") for part in name.split("/")):
        raise TimezoneError("timezone_data_unavailable", "Saat dilimi verisi kullanılamıyor.")
    try:
        with files("tzdata.zoneinfo").joinpath(*name.split("/")).open("rb") as source:
            return ZoneInfo.from_file(source, key=name)
    except (OSError, ValueError, ImportError) as error:
        raise TimezoneError("timezone_data_unavailable", "Saat dilimi verisi kullanılamıyor.") from error


def convert_to_utc(local: datetime) -> datetime:
    if local.tzinfo is None or local.utcoffset() is None:
        raise TimezoneError("invalid_datetime", "Saat dilimi içeren tarih ve saat gereklidir.")
    try:
        return local.astimezone(timezone.utc)
    except (OverflowError, ValueError) as error:
        raise TimezoneError("invalid_datetime", "Tarih UTC'ye dönüştürülemiyor.") from error


def localize_birth_datetime(birth_date: date, birth_time: time, zone: str) -> list[TimezoneCandidate]:
    if birth_time.tzinfo is not None:
        raise TimezoneError("invalid_datetime", "Yerel saat UTC offset içermemelidir.")
    wall = datetime.combine(birth_date, birth_time)
    tz = load_zone(zone)
    candidates: dict[datetime, TimezoneCandidate] = {}
    for fold in (0, 1):
        local = wall.replace(tzinfo=tz, fold=fold)
        utc = convert_to_utc(local)
        try:
            returned = utc.astimezone(tz)
        except (OverflowError, ValueError) as error:
            raise TimezoneError("invalid_datetime", "Tarih dönüştürülemiyor.") from error
        if returned.replace(tzinfo=None) == wall and utc not in candidates:
            candidates[utc] = TimezoneCandidate(
                local_datetime=local, utc_datetime=utc,
                utc_offset_minutes=local.utcoffset().total_seconds() / 60,
                dst=bool(local.dst()), fold=fold,
            )
    if not candidates:
        raise TimezoneError("nonexistent_local_time", "Bu yerel saat saat dilimi geçişinde yaşanmamıştır.", zone=zone)
    return [candidates[key] for key in sorted(candidates)]


class TimezoneService:
    def __init__(self):
        self._finder: TimezoneFinder | None = None
        self._lock = Lock()

    def resolve_timezone(self, latitude: float, longitude: float) -> str:
        if not (isfinite(latitude) and isfinite(longitude) and -90 <= latitude <= 90 and -180 <= longitude <= 180):
            raise TimezoneError("invalid_coordinates", "Koordinatlar geçerli aralıkta olmalıdır.")
        try:
            with self._lock:
                if self._finder is None:
                    self._finder = TimezoneFinder()
                zone = self._finder.timezone_at_land(lat=latitude, lng=longitude)
        except (OSError, ValueError, RuntimeError) as error:
            raise TimezoneError("timezone_data_unavailable", "Koordinat saat dilimi verisi kullanılamıyor.") from error
        if zone is None:
            raise TimezoneError("timezone_not_found", "Koordinat için kara saat dilimi bulunamadı.")
        return zone

    def resolve(self, latitude: float, longitude: float, birth_date: date, birth_time: time) -> TimezoneResponse:
        zone = self.resolve_timezone(latitude, longitude)
        candidates = localize_birth_datetime(birth_date, birth_time, zone)
        if len(candidates) > 1:
            raise TimezoneError("ambiguous_local_time", "Bu yerel saat iki farklı UTC anına karşılık geliyor.", zone=zone, candidates=candidates)
        return TimezoneResponse(timezone=zone, **candidates[0].model_dump())
