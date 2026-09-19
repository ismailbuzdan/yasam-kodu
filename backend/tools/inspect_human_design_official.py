"""Offline Stage 9A graph probes over recorded official facts, never a chart engine.

No astronomy, input endpoint, dependency installation, or golden promotion.
Prints a derived comparison; preserves all raw evidence and its original labels.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'tests/fixtures/human_design_sources'


def graph_probe(activations, structural):
    gates = {int(a['official'].split('.')[0]) for a in activations}
    aliases = {'heart': 'ego', 'splenic': 'spleen', 'solarplexus': 'solar_plexus'}
    centers = {int(k): aliases.get(v, v) for k, v in structural['gate_centers'].items()}
    channels = [pair for pair in structural['channels'] if set(pair) <= gates]
    graph = {}
    for a, b in channels:
        x, y = centers[a], centers[b]
        graph.setdefault(x, set()).add(y)
        graph.setdefault(y, set()).add(x)
    components = []
    remaining = set(graph)
    while remaining:
        seen, pending = set(), [min(remaining)]
        while pending:
            node = pending.pop()
            if node not in seen:
                seen.add(node)
                pending.extend(graph[node] - seen)
        components.append(sorted(seen))
        remaining -= seen
    reaches = lambda a, b: any(a in c and b in c for c in components)
    motor_path = any(reaches(m, 'throat') for m in ('ego', 'solar_plexus', 'sacral', 'root'))
    typ = ('Reflector' if not graph else
           ('Manifesting Generator' if motor_path else 'Generator') if 'sacral' in graph else
           'Manifestor' if motor_path else 'Projector')
    authority = ('Lunar Cycle' if not graph else 'Solar Plexus' if 'solar_plexus' in graph else
                 'Sacral' if 'sacral' in graph else 'Splenic' if 'spleen' in graph else
                 'Ego Manifested' if 'ego' in graph and typ == 'Manifestor' and reaches('ego', 'throat') else
                 'Ego Projected' if 'ego' in graph and typ == 'Projector' and any(set(c) == {25, 51} for c in channels) else
                 'Self Projected' if typ == 'Projector' and reaches('g', 'throat') else
                 'Sounding Board' if typ == 'Projector' and set(graph) <= {'head', 'ajna', 'throat'} else
                 'classification_error')
    suns = {a['side']: a['official'].split('.')[1] for a in activations if a['body'] == 'sun'}
    return {'Type': typ, 'Authority': authority,
            'Definition': ['None', 'Single', 'Split', 'Triple Split', 'Quadruple Split'][len(components)],
            'Profile': suns['personality'] + '/' + suns['design'],
            'channels': channels, 'components': components}


def build_report():
    path = ROOT / 'pyhd_official_comparison_nodes.json'
    comparison = json.loads(path.read_text())
    structural = json.loads((ROOT / 'pyhd.json').read_text())['structural']
    official = {c['case_id']: c for p in ROOT.glob('jovian_*.json') if (c := json.loads(p.read_text()))}
    rows = []
    types = {'Pure Generator': 'Generator', 'Energy Projector': 'Projector',
             'Classic Projector': 'Projector', 'Mental Projector': 'Projector'}
    authorities = {'Lunar': 'Lunar Cycle', 'Outer Authority': 'Sounding Board'}
    for c in comparison['cases']:
        actual = official[c['case_id']]['raw']['properties']
        probe = graph_probe(c['activations'], structural)
        pyhd = {'Type': types.get(c['pyhd_type'], c['pyhd_type']),
                'Authority': authorities.get(c['pyhd_authority'], c['pyhd_authority']),
                'Profile': c['pyhd_profile'],
                'Definition': ['None', 'Single', 'Split', 'Triple Split', 'Quadruple Split'][c['pyhd_components']]}
        rows.append({'case_id': c['case_id'], 'utc_datetime': c['utc_datetime'],
            'official': actual, 'pyhd_normalized': pyhd, 'proposed_graph_probe': probe,
            'pyhd_fields': {f: 'MATCH' if pyhd[f] == actual[f] else 'MISMATCH' for f in pyhd},
            'project_fields': {f: 'MATCH' if probe[f] == actual[f] else 'MISMATCH' for f in pyhd},
            'activations': {side: 'MATCH' if all(a['pyhd'] == a['official'] for a in c['activations'] if a['side'] == side) else 'MISMATCH' for side in ('personality', 'design')},
            'project_activation_calculation': 'NOT AVAILABLE',
            'nodes': [{**n, 'official_match': 'BOTH' if n['true']['gate_line'] == n['mean']['gate_line'] == n['official'] else
                       'TRUE_ONLY' if n['true']['gate_line'] == n['official'] else
                       'MEAN_ONLY' if n['mean']['gate_line'] == n['official'] else 'NEITHER'} for n in c['nodes']]})
    return {'status': 'candidate_not_approved', 'input_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
            'method': 'Independent research graph encoding from proposed rules over OFFICIAL gates and existing corroborated topology; not independent astronomy',
            'tool_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'normalization': {'types': types, 'authorities': authorities}, 'cases': rows}


if __name__ == '__main__':
    print(json.dumps(build_report(), indent=2))
