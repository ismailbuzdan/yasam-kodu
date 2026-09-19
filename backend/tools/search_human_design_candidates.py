"""Bounded synthetic research search using the existing pinned external adapter.

Outputs candidate evidence to stdout only. No production imports, no golden writes.
The source manifest must match the previously recorded SHA256 before execution.
"""
from datetime import datetime, timedelta, timezone
from enum import Enum
import hashlib
import importlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from urllib.request import urlopen

from collect_human_design_references import BASE, COMMIT, FILES, FIXTURES


def main():
    pinned = json.loads((FIXTURES / 'human_design_sources/pyhd.json').read_text())
    hashes = {r['url']: r['sha256'] for r in pinned['source_files']}
    with TemporaryDirectory(prefix='hd-rare-research-') as directory:
        root = Path(directory)
        for name in FILES:
            raw = urlopen(BASE + name, timeout=30).read()
            assert hashlib.sha256(raw).hexdigest() == hashes[BASE + name], name
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(raw)
        assert (root / 'LICENSE').read_text().startswith('MIT License')
        sys.path.insert(0, str(root / 'src'))
        if not hasattr(Enum, '_add_value_alias_'):
            def alias(member, value):
                table = member.__class__._value2member_map_
                if value in table and table[value] is not member:
                    raise ValueError('Conflicting alias')
                table[value] = member
            Enum._add_value_alias_ = alias
        pyhd = importlib.import_module('pyhd')
        import swisseph as swe
        swe.set_ephe_path(directory)
        if '--compare-official' in sys.argv:
            compare_official(pyhd, swe)
            return
        start = datetime(2000, 1, 1, 12, tzinfo=timezone.utc)
        wanted = {'Reflector', 'Manifestor', 'Ego Manifested', 'Ego Projected',
                  'Self Projected', 'Outer Authority', 'Lunar', 'definition:4',
                  'profile:2/5', 'profile:3/6', 'profile:4/1', 'profile:5/2'}
        found = set()
        results = []
        errors = []
        for day in range(366 * 6):
            stamp = start + timedelta(days=day)
            chart = pyhd.Chart(stamp)
            try:
                authority, typ = str(chart.authority), str(chart.type)
            except (ValueError, AttributeError) as error:
                errors.append({'utc_datetime': stamp.isoformat(), 'error': str(error)})
                continue
            labels = {authority, typ, f'definition:{len(chart.definitions)}',
                      f'profile:{chart.profile}'}
            gain = (labels & wanted) - found
            if gain:
                found |= gain
                results.append({'utc_datetime': stamp.isoformat(), 'covers': sorted(gain),
                                'type': typ, 'authority': authority, 'profile': str(chart.profile),
                                'definition_components': len(chart.definitions)})
                print(json.dumps(results[-1]), flush=True)
            if found == wanted:
                break
        print(json.dumps({'commit': COMMIT, 'status': 'candidate_not_approved',
                          'search': 'daily 12:00 UTC from 2000-01-01; at most 2196 days',
                          'visited': day + 1, 'missing': sorted(wanted - found),
                          'errors': errors, 'cases': results}), flush=True)


def compare_official(pyhd, swe):
    """Diagnostic adapter; external chart computation and mapper, not product rules."""
    constants = importlib.import_module('pyhd.constants')
    activation_module = importlib.import_module('pyhd.activation')
    bodies = ('sun', 'earth', 'moon', 'north_node', 'south_node', 'mercury',
              'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto')
    rows = []
    for path in sorted((FIXTURES / 'human_design_sources').glob('jovian_*.json')):
        official = json.loads(path.read_text())
        birth = datetime.fromisoformat(official['utc_datetime'])
        chart = pyhd.Chart(birth)
        row = {'case_id': official['case_id'], 'utc_datetime': birth.isoformat(),
               'official_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
               'design_datetime': chart.design.dt.isoformat(),
               'pyhd_type': str(chart.type), 'pyhd_authority': str(chart.authority),
               'pyhd_profile': str(chart.profile), 'pyhd_components': len(chart.definitions),
               'activations': [], 'nodes': []}
        for side in ('personality', 'design'):
            imprint = getattr(chart, side)
            dt = imprint.dt
            hour = dt.hour + dt.minute / 60 + (dt.second + dt.microsecond / 1e6) / 3600
            jd = swe.julday(dt.year, dt.month, dt.day, hour)
            raw = official['raw'][side + '_text'][1:]
            for planet in constants.Planets:
                body = planet._key.lower()
                a = imprint[planet]
                expected = raw[bodies.index(body)].replace(' ', '')
                row['activations'].append({'side': side, 'body': body,
                    'longitude': a.longitude, 'pyhd': f'{a.gate.num}.{a.line.num}',
                    'official': expected})
                if body not in ('north_node', 'south_node'):
                    continue
                probes = {}
                for label, node in (('true', swe.TRUE_NODE), ('mean', swe.MEAN_NODE)):
                    longitude, flags = swe.calc_ut(jd, node, swe.FLG_MOSEPH)
                    # Deliberate controlled research override: only node longitude changes.
                    probe = activation_module.Activation(planet, dt)
                    probe.longitude = (longitude[0] + (180 if body == 'south_node' else 0)) % 360
                    probe.angle = (probe.longitude - constants.GATE_WHEEL_START_DEGREES) % 360
                    probe._compute_data()
                    probes[label] = {'longitude': probe.longitude, 'flags': flags,
                                     'gate_line': f'{probe.gate.num}.{probe.line.num}'}
                row['nodes'].append({'side': side, 'body': body, 'official': expected, **probes})
        rows.append(row)
    print(json.dumps({'status': 'candidate_not_approved', 'retrieved_at': datetime.now(timezone.utc).isoformat(),
        'tool': 'tools/search_human_design_candidates.py --compare-official',
        'tool_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'commit': COMMIT, 'version': pyhd.__version__, 'python': sys.version,
        'source_manifest': 'human_design_sources/pyhd.json; every upstream source hash checked',
        'adapter': 'Enum value-alias shim; node probes override longitude/angle only before upstream mapper',
        'ephemeris': f'Swiss {swe.version}; Moshier; no ephemeris files',
        'independence': 'PyHD rerun shares original implementation; official outputs are separate opaque pipeline',
        'cases': rows}), flush=True)


if __name__ == '__main__':
    main()
