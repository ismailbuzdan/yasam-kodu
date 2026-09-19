"""Production graph/classification tests. Synthetic charts and structural inputs only."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import FrozenInstanceError, fields, replace
from datetime import datetime, timezone
import inspect
import json
from pathlib import Path

import pytest

from app.services import human_design_core as hd
from app.services.human_design_models import Activation, AstronomyResult, DesignMoment, HumanDesignError

ROOT = Path(__file__).parent / 'fixtures'
CONVENTIONS = json.loads((ROOT / 'human_design_conventions.json').read_text())
REFS = json.loads((ROOT / 'human_design_references.json').read_text())
NORMALIZE = REFS['acceptance_policy']['normalization']
STAMP = datetime(2000, 3, 20, tzinfo=timezone.utc)


def synthetic(gates=(), pair=(1, 3)):
    # Structural probe, not an astronomical chart. Sun uses an already active gate,
    # or a lone Gate 1 for the zero-channel case; cannot accidentally add an edge.
    seed = gates[0] if gates else 1
    personality = tuple(Activation('moon', 0, g, 1) for g in gates) + (Activation('sun', 0, seed, pair[0]),)
    design = (Activation('sun', 0, seed, pair[1]),)
    return AstronomyResult(2451545, DesignMoment(2451457, 0, 0, 1), STAMP, personality, design)


@pytest.mark.parametrize('vector', CONVENTIONS['graph_vectors'], ids=lambda v: v['id'])
def test_18_structural_vectors(vector):
    result = hd.classify_astronomy(synthetic(vector['gates']))
    expected = vector['expected']
    assert result.type == NORMALIZE['types'][expected['Type']]
    assert result.authority == NORMALIZE['authorities'][expected['Authority']]
    assert result.definition == NORMALIZE['definition'][expected['Definition']]
    assert result.strategy == {'generator': 'wait_to_respond', 'manifesting_generator': 'wait_to_respond',
        'manifestor': 'inform', 'projector': 'wait_for_invitation', 'reflector': 'wait_lunar_cycle'}[result.type]
    assert result.component_count == len(result.definition_components)
    assert result.defined_centers == tuple(sorted(result.defined_centers))
    assert result.undefined_centers == tuple(sorted(result.undefined_centers))
    assert result.definition_components == tuple(sorted(result.definition_components))


def test_topology_integrity_against_existing_evidence():
    structural = json.loads((ROOT / 'human_design_sources/pyhd.json').read_text())['structural']
    aliases = {'heart': 'ego', 'splenic': 'spleen', 'solarplexus': 'solar_plexus'}
    assert dict(hd.GATE_CENTER) == {int(k): aliases.get(v, v) for k, v in structural['gate_centers'].items()}
    assert hd.CHANNELS == tuple(tuple(c) for c in structural['channels'])
    gates = [g for values in hd.CENTER_GATES.values() for g in values]
    assert len(gates) == len(set(gates)) == 64
    assert set(gates) == set(range(1, 65))
    assert len(hd.CENTER_GATES) == 9
    assert len(hd.CHANNELS) == len(set(hd.CHANNELS)) == 36
    assert hd.CHANNELS == tuple(sorted(hd.CHANNELS))


@pytest.mark.parametrize('channel', hd.CHANNELS)
def test_each_channel_cross_imprint_and_lone_gate(channel):
    a, b = channel
    probe = synthetic((a,))
    lone = hd.classify_astronomy(probe)
    assert lone.channels == lone.defined_centers == lone.definition_components == ()
    assert lone.definition == 'none'
    assert len(lone.undefined_centers) == 9
    probe = replace(probe, design_activations=(Activation('sun', 0, b, 3),))
    result = hd.classify_astronomy(probe)
    assert result.channels == (channel,)
    assert result.defined_centers == tuple(sorted((hd.GATE_CENTER[a], hd.GATE_CENTER[b])))
    assert result.active_gates == tuple(sorted(channel))


def test_duplicates_order_and_component_not_channel_count():
    probe = synthetic((1, 8, 25, 51, 1, 8))
    result = hd.classify_astronomy(probe)
    assert result.active_gates == (1, 8, 25, 51)
    assert len(result.channels) == 2 and result.component_count == 1
    assert result.definition == 'single'
    reordered = replace(probe, personality=tuple(reversed(probe.personality)))
    assert hd.classify_astronomy(reordered) == result
    assert len(probe.personality) == 7  # original planetary duplicates preserved


@pytest.mark.parametrize('gates', [(18, 58, 25, 51), (18, 58, 1, 8),
                                    (18, 58, 4, 63), (18, 58, 21, 45)])
def test_splenic_over_lower_authorities(gates):
    assert hd.classify_astronomy(synthetic(gates)).authority == 'splenic'


@pytest.mark.parametrize('label', CONVENTIONS['allowed_profiles'])
def test_all_profiles_using_sun_body_not_position(label):
    pair = tuple(map(int, label.split('/')))
    result = hd.classify_astronomy(synthetic((3, 60), pair))
    assert result.profile.label == label
    assert (result.profile.personality_line, result.profile.design_line) == pair


@pytest.mark.parametrize('fault', ['pair', 'missing_sun', 'duplicate_sun', 'gate', 'line', 'boolean'])
def test_classification_errors(fault):
    probe = synthetic((3, 60))
    if fault == 'pair':
        probe = synthetic((3, 60), (1, 1))
    elif fault == 'missing_sun':
        probe = replace(probe, design_activations=())
    elif fault == 'duplicate_sun':
        probe = replace(probe, design_activations=probe.design_activations * 2)
    else:
        invalid = Activation('moon', 0, 65 if fault == 'gate' else True if fault == 'boolean' else 3,
                             7 if fault == 'line' else 1)
        probe = replace(probe, personality=probe.personality + (invalid,))
    with pytest.raises(HumanDesignError) as caught:
        hd.classify_astronomy(probe)
    assert caught.value.code == 'classification_error'


def test_unclassifiable_authority_fails_instead_of_guessing():
    with pytest.raises(HumanDesignError) as caught:
        hd._authority('projector', {'root'}, (), (('root',),))
    assert caught.value.code == 'classification_error'


@pytest.mark.parametrize('case', REFS['accepted_expectations'], ids=lambda c: c['case_id'])
def test_official_complete_regression(case):
    result = hd.calculate_human_design_core(datetime.fromisoformat(case['utc_datetime']))
    for field in ('type', 'authority', 'definition'):
        assert getattr(result, field) == case['expected'][field]
    assert result.profile.label == case['expected']['profile']
    for side, actual in [('personality', result.astronomy.personality), ('design', result.astronomy.design_activations)]:
        assert [{'body': a.body, 'gate': a.gate, 'line': a.line} for a in actual] == case['expected'][side]


def test_orchestration_once_immutability_metadata_and_privacy(monkeypatch):
    original = hd.calculate_activations
    calls = []
    def spy(stamp):
        value = original(stamp)
        calls.append(value)
        return value
    monkeypatch.setattr(hd, 'calculate_activations', spy)
    result = hd.calculate_human_design_core(STAMP)
    assert len(calls) == 1 and result.astronomy is calls[0]
    assert result.birth_utc == STAMP
    assert result.metadata.spec_revision == 'stage9a2-v1'
    assert result.metadata.pyswisseph_version == '2.10.3.2'
    assert result.metadata.swiss_ephemeris_version == '2.10.03'
    assert result.metadata.node_algorithm == 'true_node'
    with pytest.raises(FrozenInstanceError):
        result.profile.label = '1/1'
    with pytest.raises(FrozenInstanceError):
        result.type = 'projector'
    assert list(inspect.signature(hd.calculate_human_design_core).parameters) == ['birth_utc']
    assert not {'name', 'birthplace', 'latitude', 'longitude'} & {f.name for f in fields(result)}


def test_complete_determinism_and_concurrency():
    stamps = [datetime.fromisoformat(c['utc_datetime']) for c in REFS['accepted_expectations'][:4]]
    expected = [hd.calculate_human_design_core(t) for t in stamps]
    assert expected == [hd.calculate_human_design_core(t) for t in stamps]
    with ThreadPoolExecutor(max_workers=4) as pool:
        actual = list(pool.map(hd.calculate_human_design_core, stamps * 2))
    assert actual == expected * 2
