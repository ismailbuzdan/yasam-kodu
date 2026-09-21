"""Allowlist-only projection from immutable K1A values to the public contract."""
from app.schemas.kameri import (
    AbjadResponse, AstronomyResponse, HijriResponse, KameriMetadataResponse,
    KameriResponse, LunarResponse, MansionResponse, PlanetaryHourAssumptionsResponse,
    PlanetaryHourIntervalResponse, PlanetaryHourResponse,
)
from app.services.traditional.models import AbjadResult, HijriResult, LunarResult, PlanetaryHourResult


def project_kameri(hijri: HijriResult, lunar: LunarResult, abjad: AbjadResult,
                    planetary_hour: PlanetaryHourResult) -> KameriResponse:
    astronomy = AstronomyResponse(
        pyswisseph_version=lunar.metadata.pyswisseph_version,
        swiss_ephemeris_version=lunar.metadata.swiss_ephemeris_version,
        ephemeris=lunar.metadata.ephemeris,
        frame=lunar.metadata.frame,
    )
    return KameriResponse(
        metadata=KameriMetadataResponse(
            schema_version="kameri-code-v1",
            calculation_layers=("hijri", "lunar", "abjad", "planetary_hour"),
            interpretation_present=False,
        ),
        hijri=HijriResponse(
            hijri_year=hijri.hijri_year, hijri_month=hijri.hijri_month, hijri_day=hijri.hijri_day,
            method_id=hijri.method_id, method_version=hijri.method_version,
            calendar_type=hijri.calendar_type, classification=hijri.classification,
            day_boundary=hijri.day_boundary, input_owner=hijri.input_owner,
            limitation=hijri.limitation,
        ),
        lunar=LunarResponse(
            sun_longitude=lunar.sun_longitude, moon_longitude=lunar.moon_longitude,
            elongation=lunar.elongation, illuminated_fraction=lunar.illuminated_fraction,
            phase=lunar.phase,
            mansion=MansionResponse(
                index=lunar.mansion.index, method_id=lunar.mansion.method_id,
                method_version=lunar.mansion.method_version, mapping_kind=lunar.mansion.mapping_kind,
                classification=lunar.mansion.classification, rule_origin=lunar.mansion.rule_origin,
                limitation=lunar.mansion.limitation,
            ),
            astronomy=astronomy, method_id=lunar.method_id, method_version=lunar.method_version,
            classification=lunar.classification, label_policy=lunar.label_policy,
            label_rule_origin=lunar.label_rule_origin, limitation=lunar.limitation,
        ),
        abjad=AbjadResponse(
            raw_sum=abjad.raw_sum, method_id=abjad.method_id, normalization_id=abjad.normalization_id,
            method_version=abjad.method_version, classification=abjad.classification,
            limitation=abjad.limitation,
        ),
        planetary_hour=PlanetaryHourResponse(
            interval=PlanetaryHourIntervalResponse(
                period=planetary_hour.interval.period, hour=planetary_hour.interval.hour,
                total_offset=planetary_hour.interval.total_offset, ruler=planetary_hour.interval.ruler,
            ),
            planetary_date=planetary_hour.planetary_date, timezone_id=planetary_hour.timezone_id,
            method_id=planetary_hour.method_id, method_version=planetary_hour.method_version,
            classification=planetary_hour.classification,
            event_classification=planetary_hour.event_classification,
            rule_origin=planetary_hour.rule_origin, limitation=planetary_hour.limitation,
            assumptions=PlanetaryHourAssumptionsResponse(
                observer_height_m=planetary_hour.assumptions.observer_height_m,
                pressure_hpa=planetary_hour.assumptions.pressure_hpa,
                temperature_c=planetary_hour.assumptions.temperature_c,
                limb=planetary_hour.assumptions.limb,
                refraction=planetary_hour.assumptions.refraction,
                horizon=planetary_hour.assumptions.horizon,
            ),
        ),
    )
