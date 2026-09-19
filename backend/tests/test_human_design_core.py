"""Production core tests: no research engine imports, no classification expectations."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError
from datetime import datetime, timedelta, timezone
from fractions import Fraction
import json
import math
from pathlib import Path

import pytest
import swisseph as swe

from app.services import astrology_service as astrology
from app.schemas.astrology import AstrologyRequest
from app.services import human_design_astronomy as hd
from app.services.human_design_mapping import GATE_SEQUENCE, gate_line
from app.services.human_design_models import HumanDesignError

ROOT = Path(__file__).parent / 'fixtures'
CONVENTIONS = json.loads((ROOT / 'human_design_conventions.json').read_text())
REFERENCES = json.loads((ROOT / 'human_design_references.json').read_text())['accepted_expectations']
STAMP = datetime(2000, 3, 20, tzinfo=timezone.utc)


def test_all_exact_boundaries_and_neighbors():
    assert list(GATE_SEQUENCE) == CONVENTIONS['sequence']
    seen = set()
    for index in range(384):
        edge = float((Fraction(302) + index * Fraction(15, 16)) % 360)
        expected = (GATE_SEQUENCE[index // 6], index % 6 + 1)
        previous = (index - 1) % 384
        assert gate_line(edge) == expected
        assert gate_line(math.nextafter(edge, math.inf)) == expected
        assert gate_line(math.nextafter(edge, -math.inf)) == (GATE_SEQUENCE[previous // 6], previous % 6 + 1)
        seen.add(expected)
    assert len(seen) == 384
    assert {g for g, _ in seen} == set(range(1, 65))


def test_mapping_vectors_and_normalization():
    for longitude, gate, line in CONVENTIONS['boundary_vectors']:
        assert gate_line(longitude) == (gate, line)
    for value in (0, 360, -360, 720, -720):
        assert gate_line(value) == (25, 2)
    assert gate_line(-58) == gate_line(302) == (41, 1)
    assert gate_line(math.nextafter(0, -math.inf)) == (25, 2)


@pytest.mark.parametrize('value', [math.nan, math.inf, -math.inf])
def test_mapper_nonfinite(value):
    with pytest.raises(HumanDesignError) as caught:
        gate_line(value)
    assert caught.value.code == 'ephemeris_error'


@pytest.mark.parametrize('case', REFERENCES, ids=lambda c: c['case_id'])
def test_official_26_activations(case):
    result = hd.calculate_activations(datetime.fromisoformat(case['utc_datetime']))
    for field, actual in [('personality', result.personality), ('design', result.design_activations)]:
        assert [{'body': a.body, 'gate': a.gate, 'line': a.line} for a in actual] == case['expected'][field]


@pytest.mark.parametrize('stamp', [STAMP, datetime(1800, 1, 1, tzinfo=timezone.utc),
    datetime(2100, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc),
    datetime(2000, 7, 1, tzinfo=timezone.utc)])
def test_solver_real_dates_and_determinism(stamp):
    result = hd.calculate_activations(stamp)
    assert result == hd.calculate_activations(stamp)
    assert result.design_utc < stamp
    assert 80 <= result.personality_jd_ut1 - result.design.jd_ut1 <= 100
    assert abs(result.personality_jd_ut1 - result.design.jd_ut1 - 88) > 0.01
    assert result.design.bracket_seconds <= 0.01
    assert abs(result.design.residual_degrees) <= 1e-7
    assert 1 <= result.design.iterations <= 64
    arc = (result.personality[0].longitude - result.design_activations[0].longitude) % 360
    assert abs(arc - 88) <= 1e-7
    with pytest.raises(FrozenInstanceError):
        result.personality[0].gate = 2


@pytest.mark.parametrize('stamp,code', [(datetime(2000, 1, 1), 'invalid_utc_datetime'),
    (STAMP.replace(tzinfo=timezone(timedelta(hours=1))), 'invalid_utc_datetime'),
    (STAMP.replace(year=1799), 'unsupported_date_range'),
    (STAMP.replace(year=2101), 'unsupported_date_range'), (None, 'invalid_utc_datetime')])
def test_input_rejected(stamp, code):
    with pytest.raises(HumanDesignError) as caught:
        hd.calculate_activations(stamp)
    assert caught.value.code == code


def test_native_bodies_flags_true_node_and_oppositions(monkeypatch):
    original = swe.calc_ut
    calls = []
    def spy(jd, body, flags):
        calls.append((jd, body, flags))
        return original(jd, body, flags)
    monkeypatch.setattr(swe, 'calc_ut', spy)
    result = hd.calculate_activations(STAMP)
    assert all(flags == swe.FLG_MOSEPH | swe.FLG_SPEED for _, _, flags in calls)
    assert {b for _, b, _ in calls} == set(hd.NATIVE_BODIES.values())
    assert swe.TRUE_NODE in {b for _, b, _ in calls}
    for side in (result.personality, result.design_activations):
        assert tuple(a.body for a in side) == hd.BODIES
        positions = {a.body: a.longitude for a in side}
        assert all(0 <= p < 360 for p in positions.values())
        assert positions['earth'] == (positions['sun'] + 180) % 360
        assert positions['south_node'] == (positions['north_node'] + 180) % 360
    with astrology._LOCK:
        astrology.initialize_ephemeris()
        actual = original(result.personality_jd_ut1, swe.TRUE_NODE, hd.FLAGS)[0][0]
        assert result.personality[3].longitude == actual
        mean = original(result.personality_jd_ut1, swe.MEAN_NODE, hd.FLAGS)[0][0]
        assert gate_line(mean) != (result.personality[3].gate, result.personality[3].line)
        swe.set_topo(100, 60, 3000)
    assert result == hd.calculate_activations(STAMP)


@pytest.mark.parametrize('fault', ['native', 'flags', 'nan', 'sun_speed', 'init', 'jd', 'utc'])
def test_ephemeris_failures_are_typed_and_sanitized(monkeypatch, fault):
    if fault in ('native', 'flags', 'nan', 'sun_speed'):
        def broken(*args):
            if fault == 'native':
                raise swe.Error('private native details')
            return (math.nan if fault == 'nan' else 12, 0, 0, -1 if fault == 'sun_speed' else 1, 0, 0), (swe.FLG_SWIEPH if fault == 'flags' else hd.FLAGS)
        monkeypatch.setattr(swe, 'calc_ut', broken)
    elif fault == 'init':
        monkeypatch.setenv('SE_EPHE_PATH', 'forbidden')
    elif fault == 'jd':
        monkeypatch.setattr(swe, 'utc_to_jd', lambda *a: (0, math.nan))
    else:
        monkeypatch.setattr(swe, 'jdut1_to_utc', lambda *a: (_ for _ in ()).throw(swe.Error('private native details')))
    with pytest.raises(HumanDesignError) as caught:
        hd.calculate_activations(STAMP)
    assert caught.value.code == ('design_moment_error' if fault == 'sun_speed' else 'ephemeris_error')
    assert 'private' not in str(caught.value)


@pytest.mark.parametrize('sun_at', [lambda t: math.nan, lambda t: 200,
    lambda t: (100-t) % 360, lambda t: (180 if t < -88 else 0),
    lambda t: (11 if t < -88 else 13)])
def test_solver_rejects_invalid_progression_or_discontinuity(sun_at):
    with pytest.raises(HumanDesignError) as caught:
        hd.solve_design_moment(0, 100, sun_at)
    assert caught.value.code == 'design_moment_error'


def test_solver_iteration_limit_and_stagnation(monkeypatch):
    monkeypatch.setattr(hd, 'MAX_ITERATIONS', 1)
    with pytest.raises(HumanDesignError, match='converge'):
        hd.solve_design_moment(100, 100, lambda t: t % 360)
    monkeypatch.setattr(hd, 'MAX_ITERATIONS', 64)
    with pytest.raises(HumanDesignError):
        hd.solve_design_moment(1e20, 100, lambda t: t % 360)


def test_serialization_half_even_and_not_fed_back(monkeypatch):
    baseline = hd.calculate_activations(STAMP)
    monkeypatch.setattr(hd, '_serialize_utc', lambda jd: STAMP)
    modified = hd.calculate_activations(STAMP)
    assert modified.design == baseline.design
    assert modified.design_activations == baseline.design_activations
    assert modified.design_utc == STAMP


@pytest.mark.parametrize('seconds,microsecond', [(1/128, 7812), (3/128, 23438)])
def test_half_even_exact_ties(monkeypatch, seconds, microsecond):
    monkeypatch.setattr(swe, 'jdut1_to_utc', lambda *a: (2000, 1, 1, 0, 0, seconds))
    assert hd._serialize_utc(2451545).microsecond == microsecond


def test_shared_native_state_concurrency():
    request = AstrologyRequest(utc_datetime=STAMP, latitude=0, longitude=0)
    service = astrology.AstrologyService()
    astro_expected = service.calculate(request)
    expected = hd.calculate_activations(STAMP)
    def work(i):
        return hd.calculate_activations(STAMP) if i % 2 == 0 else service.calculate(request)
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(work, range(8)))
    for i, result in enumerate(results):
        assert result == (expected if i % 2 == 0 else astro_expected)
