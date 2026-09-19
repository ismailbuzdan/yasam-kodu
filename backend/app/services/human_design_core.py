"""ADR-015 mechanical classification, independently encoded from the project spec.

Consumes existing astronomy once. No external HD implementation, fixture I/O,
interpretation, native calls, person identifiers, coordinates or logging.
"""
from dataclasses import fields
from collections.abc import Mapping
from datetime import datetime
from importlib.metadata import version
from types import MappingProxyType

import swisseph as swe

from app.services.human_design_astronomy import calculate_activations
from app.services.human_design_models import (
    Activation, AstronomyResult, Authority, Center, DefinitionKind, HDType,
    HumanDesignError, HumanDesignMetadata, HumanDesignResult, Mechanics, Profile, Strategy,
)

CENTER_GATES: Mapping[Center, tuple[int, ...]] = MappingProxyType({
    'head': (61, 63, 64), 'ajna': (4, 11, 17, 24, 43, 47),
    'throat': (8, 12, 16, 20, 23, 31, 33, 35, 45, 56, 62),
    'g': (1, 2, 7, 10, 13, 15, 25, 46), 'ego': (21, 26, 40, 51),
    'sacral': (3, 5, 9, 14, 27, 29, 34, 42, 59),
    'solar_plexus': (6, 22, 30, 36, 37, 49, 55),
    'spleen': (18, 28, 32, 44, 48, 50, 57),
    'root': (19, 38, 39, 41, 52, 53, 54, 58, 60),
})
GATE_CENTER = MappingProxyType({gate: center for center, gates in CENTER_GATES.items() for gate in gates})
CHANNELS = (
    (1, 8), (2, 14), (3, 60), (4, 63), (5, 15), (6, 59), (7, 31), (9, 52),
    (10, 20), (10, 34), (10, 57), (11, 56), (12, 22), (13, 33), (16, 48),
    (17, 62), (18, 58), (19, 49), (20, 34), (20, 57), (21, 45), (23, 43),
    (24, 61), (25, 51), (26, 44), (27, 50), (28, 38), (29, 46), (30, 41),
    (32, 54), (34, 57), (35, 36), (37, 40), (39, 55), (42, 53), (47, 64),
)
MOTORS = frozenset(('sacral', 'ego', 'solar_plexus', 'root'))
STRATEGIES: Mapping[HDType, Strategy] = MappingProxyType({
    'generator': 'wait_to_respond', 'manifesting_generator': 'wait_to_respond',
    'manifestor': 'inform', 'projector': 'wait_for_invitation', 'reflector': 'wait_lunar_cycle',
})
DEFINITIONS: tuple[DefinitionKind, ...] = ('none', 'single', 'split', 'triple_split', 'quadruple_split')
PROFILES = frozenset(((1, 3), (1, 4), (2, 4), (2, 5), (3, 5), (3, 6),
                      (4, 6), (4, 1), (5, 1), (5, 2), (6, 2), (6, 3)))


def _sun_line(activations: tuple[Activation, ...]) -> int:
    suns = [a.line for a in activations if a.body == 'sun']
    if len(suns) != 1:
        raise HumanDesignError('classification_error', 'Exactly one Sun per imprint is required.')
    return suns[0]


def _authority(typ: HDType, centers: set[Center], channels: tuple[tuple[int, int], ...],
               components: tuple[tuple[Center, ...], ...]) -> Authority:
    def reaches(a: Center, b: Center) -> bool:
        return any(a in part and b in part for part in components)
    if typ == 'reflector':
        return 'lunar'
    if 'solar_plexus' in centers:
        return 'emotional'
    if 'sacral' in centers:
        return 'sacral'
    if 'spleen' in centers:
        return 'splenic'
    if typ == 'manifestor' and 'ego' in centers and reaches('ego', 'throat'):
        return 'ego_manifested'
    if typ == 'projector' and (25, 51) in channels:
        return 'ego_projected'
    if typ == 'projector' and reaches('g', 'throat'):
        return 'self_projected'
    if typ == 'projector' and centers <= {'head', 'ajna', 'throat'}:
        return 'mental_environmental'
    raise HumanDesignError('classification_error', 'No valid authority for the defined graph.')


def classify_astronomy(astronomy: AstronomyResult) -> Mechanics:
    """Pure mechanical derivation. Imprint lists and their ordering are not modified."""
    activations = astronomy.personality + astronomy.design_activations
    if any(type(a.gate) is not int or not 1 <= a.gate <= 64 or
           type(a.line) is not int or not 1 <= a.line <= 6 for a in activations):
        raise HumanDesignError('classification_error', 'Invalid activation gate or line.')
    pair = (_sun_line(astronomy.personality), _sun_line(astronomy.design_activations))
    if pair not in PROFILES:
        raise HumanDesignError('classification_error', 'Unsupported Profile pair.')
    gates = {a.gate for a in activations}
    channels = tuple((a, b) for a, b in CHANNELS if a in gates and b in gates)
    graph: dict[Center, set[Center]] = {}
    for a, b in channels:
        left, right = GATE_CENTER[a], GATE_CENTER[b]
        graph.setdefault(left, set()).add(right)
        graph.setdefault(right, set()).add(left)
    remaining = set(graph)
    parts = []
    while remaining:
        pending, visited = [min(remaining)], set()
        while pending:
            center = pending.pop()
            if center not in visited:
                visited.add(center)
                pending.extend(graph[center] - visited)
        parts.append(tuple(sorted(visited)))
        remaining -= visited
    components = tuple(sorted(parts))
    if len(components) > 4:
        raise HumanDesignError('classification_error', 'Unsupported Definition component count.')
    centers = set(graph)
    motor_reaches = any('throat' in part and MOTORS.intersection(part) for part in components)
    typ: HDType
    if not centers:
        typ = 'reflector'
    elif 'sacral' in centers:
        typ = 'manifesting_generator' if motor_reaches else 'generator'
    else:
        typ = 'manifestor' if motor_reaches else 'projector'
    return Mechanics(tuple(sorted(gates)), channels, tuple(sorted(centers)),
        tuple(sorted(set(CENTER_GATES) - centers)), typ, STRATEGIES[typ],
        _authority(typ, centers, channels, components), Profile(*pair, f'{pair[0]}/{pair[1]}'),
        DEFINITIONS[len(components)], components)


def calculate_human_design_core(birth_utc: datetime) -> HumanDesignResult:
    astronomy = calculate_activations(birth_utc)
    mechanics = classify_astronomy(astronomy)
    metadata = HumanDesignMetadata(version('pyswisseph'), swe.version)
    return HumanDesignResult(**{f.name: getattr(mechanics, f.name) for f in fields(Mechanics)},
                             birth_utc=birth_utc, astronomy=astronomy, metadata=metadata)
