"""Offline admission, provenance and immutable-snapshot regression for ADR-020."""

import ast
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from pydantic import ValidationError

from app.knowledge.kameri.models import KnowledgeBase
from app.knowledge.kameri.repository import (
    ClaimNotFoundError, get_claim, get_knowledge_base,
)

PACKAGE = Path(__file__).resolve().parents[1] / 'app/knowledge/kameri'
DATA = PACKAGE / 'data/kameri_kb_v1.json'
EXPECTED = {'ASMA_NUM_001', 'HIJRI_CTX_001', 'HIJRI_CTX_002', 'HIJRI_CTX_003'}


def dataset():
    return json.loads(DATA.read_text(encoding='utf-8'))


def test_exact_qualified_inventory_and_provenance():
    kb = get_knowledge_base()
    assert kb.schema_version == 'kameri-kb-v1'
    assert {claim.claim_id for claim in kb.claims} == EXPECTED
    assert len(kb.claims) == len(kb.sources) == 4
    sources = {source.source_id: source for source in kb.sources}
    assert set(sources) == {'KI-A03', 'KI-B05', 'KI-B07', 'KI-B08'}
    for claim in kb.claims:
        assert claim.kb_version == kb.schema_version
        assert claim.ai_usage == 'restricted'
        assert claim.limitations and claim.does_not_support and claim.religious_claim_boundary
        for ref in claim.source_refs:
            assert ref.locator.strip()
            source = sources[ref.source_id]
            assert source.url.startswith('https://')
            assert source.title and source.locator and source.verified_scope


def test_production_matches_qualified_research_ledger():
    default = Path(__file__).resolve().parents[2] / 'docs/references/kameri_interpretation_sources.json'
    ledger_path = Path(os.environ.get('KAMERI_RESEARCH_LEDGER', str(default)))
    # Docker mounts backend only. Supply the real ledger explicitly, never skip this gate.
    ledger = json.loads(ledger_path.read_text(encoding='utf-8'))
    qualified = {c['claim_id']: c for c in ledger['claims'] if c['status'] == 'QUALIFIED_FOR_KB'}
    excluded = {c['claim_id'] for c in ledger['claims'] if c['status'] != 'QUALIFIED_FOR_KB'}
    assert set(qualified) == EXPECTED
    assert len(excluded) == 14
    assert excluded.isdisjoint(c.claim_id for c in get_knowledge_base().claims)
    for claim in get_knowledge_base().claims:
        research = qualified[claim.claim_id]
        for field in ('feature', 'method_id', 'tradition_id', 'classification', 'claim_type',
                      'statement', 'normalized_theme', 'original_context',
                      'religious_claim_boundary', 'ai_usage'):
            assert getattr(claim, field) == research[field]
        assert claim.limitations == tuple(research['limitations'])
        assert claim.does_not_support == tuple(research['does_not_support'])
        assert [ref.model_dump() for ref in claim.source_refs] == research['locators']
    sources = {s['source_id']: s for s in ledger['sources']}
    for source in get_knowledge_base().sources:
        for field, value in source.model_dump().items():
            assert value == sources[source.source_id][field]


@pytest.mark.parametrize('claim_id', sorted(EXPECTED))
def test_lookup_is_stable_and_explicit(claim_id):
    assert get_claim(claim_id) is get_claim(claim_id)
    assert get_claim(claim_id).claim_id == claim_id


@pytest.mark.parametrize('claim_id', ['MAN_INT_001', 'HOUR_INT_001', 'PERSONAL_ASMA_001',
                                    'ZOD_POP_001', 'HIJRI_PERSON_001', 'MOTHER_001',
                                    'unknown', '', 66, None])
def test_missing_lookup_is_typed_and_private(claim_id):
    with pytest.raises(ClaimNotFoundError, match='^Qualified claim not found$'):
        get_claim(claim_id)


@pytest.mark.parametrize('field', ['source_text', 'quote', 'raw_passage', 'full_text', 'status'])
def test_unapproved_fields_rejected(field):
    payload = dataset()
    payload['claims'][0][field] = 'not admitted'
    with pytest.raises(ValidationError):
        KnowledgeBase.model_validate_json(json.dumps(payload))


@pytest.mark.parametrize('field,value', [
    ('ai_usage', 'allowed'), ('ai_usage', 'forbidden'), ('application_mode', 'abjad_match'),
    ('application_mode', 'hijri_month_context'), ('application_key', 9),
    ('claim_id', 'MAN_INT_001'), ('classification', 'CULTURAL_CONTEXT'),
    ('limitations', []), ('does_not_support', []), ('religious_claim_boundary', ' '),
    ('source_refs', []), ('kb_version', 'kameri-kb-v2'),
])
def test_invalid_claim_policy_rejected(field, value):
    payload = dataset()
    claim = next(c for c in payload['claims'] if c['claim_id'] == 'ASMA_NUM_001')
    claim[field] = value
    with pytest.raises(ValidationError):
        KnowledgeBase.model_validate_json(json.dumps(payload))


@pytest.mark.parametrize('month', [None, 1, 12])
def test_ramadan_cannot_be_reassigned(month):
    payload = dataset()
    next(c for c in payload['claims'] if c['claim_id'] == 'HIJRI_CTX_001')['application_key'] = month
    with pytest.raises(ValidationError):
        KnowledgeBase.model_validate_json(json.dumps(payload))


@pytest.mark.parametrize('defect', ['duplicate_claim', 'missing_claim', 'missing_source',
                                   'duplicate_source', 'missing_locator', 'unknown_source',
                                   'duplicate_ref', 'unused_source', 'version'])
def test_invalid_dataset_fails_closed(defect):
    payload = dataset()
    if defect == 'duplicate_claim':
        payload['claims'].append(payload['claims'][0])
    elif defect == 'missing_claim':
        payload['claims'].pop()
    elif defect == 'missing_source':
        payload['sources'].pop()
    elif defect == 'duplicate_source':
        payload['sources'][0] = payload['sources'][1]
    elif defect == 'missing_locator':
        payload['claims'][0]['source_refs'][0]['locator'] = ' '
    elif defect == 'unknown_source':
        payload['claims'][0]['source_refs'][0]['source_id'] = 'KI-B99'
    elif defect == 'duplicate_ref':
        refs = payload['claims'][0]['source_refs']
        refs.append(refs[0])
    elif defect == 'unused_source':
        for claim in payload['claims']:
            claim['source_refs'] = [ref for ref in claim['source_refs'] if ref['source_id'] != 'KI-A03']
    else:
        payload['schema_version'] = 'unknown'
    with pytest.raises(ValidationError):
        KnowledgeBase.model_validate_json(json.dumps(payload))


def test_rights_boundary_has_no_source_prose_fields():
    forbidden = {'source_text', 'quote', 'raw_passage', 'full_text', 'scan', 'translation', 'table'}

    def inspect(value):
        if isinstance(value, dict):
            assert forbidden.isdisjoint(value)
            for child in value.values():
                inspect(child)
        elif isinstance(value, list):
            for child in value:
                inspect(child)

    inspect(dataset())
    assert all(len(c.statement) <= 300 for c in get_knowledge_base().claims)


def test_nested_mutation_cannot_change_the_snapshot():
    kb = get_knowledge_base()
    original = kb.model_dump_json()
    claim = get_claim('ASMA_NUM_001')
    for obj, field, value in [(kb, 'claims', ()), (claim, 'application_mode', 'hijri_month_context'),
                              (claim.source_refs[0], 'locator', 'changed'),
                              (kb.sources[0], 'title', 'changed')]:
        with pytest.raises(ValidationError):
            setattr(obj, field, value)
    with pytest.raises(TypeError):
        claim.limitations[0] = 'changed'
    with pytest.raises(TypeError):
        kb.claims[0] = claim
    exported = kb.model_dump(mode='json')
    exported['claims'][0]['source_refs'][0]['locator'] = 'changed'
    assert get_knowledge_base() is kb
    assert kb.model_dump_json() == original


def test_concurrent_selection_and_reference_lookup_are_isolated():
    from app.knowledge.kameri.models import HijriMonthContext
    from app.knowledge.kameri.selector import select_knowledge

    def read(key):
        if key == 'reference':
            return get_claim('ASMA_NUM_001').model_dump_json()
        return select_knowledge(HijriMonthContext(hijri_month=key)).model_dump_json()

    keys = [9, 12, 1, 'reference'] * 20
    expected = [read(key) for key in keys]
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert list(pool.map(read, keys)) == expected


def test_package_has_no_calculation_or_network_imports():
    # Closed dependency boundary: adding an engine/provider requires an explicit decision.
    allowed = {'typing', 'pydantic', 'pathlib'}
    for path in PACKAGE.glob('*.py'):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Import):
                assert all(alias.name.split('.')[0] in allowed for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert node.level == 1 or node.module.split('.')[0] in allowed


def test_fresh_process_works_without_network_research_or_calculation():
    script = '''
import builtins
import pathlib
import socket
import sys
original_open = __import__('io').open
def offline_open(file, *args, **kwargs):
    if 'research' in str(file) or 'docs' in pathlib.Path(str(file)).parts:
        raise AssertionError('Research access forbidden')
    return original_open(file, *args, **kwargs)
__import__('io').open = offline_open
def forbidden(*args, **kwargs):
    raise AssertionError('Network forbidden')
socket.socket = forbidden
socket.create_connection = forbidden
original_import = builtins.__import__
def guarded_import(name, *args, **kwargs):
    if name.startswith(('app.services', 'swisseph', 'httpx', 'requests', 'urllib')):
        raise AssertionError('Engine/provider import forbidden')
    return original_import(name, *args, **kwargs)
builtins.__import__ = guarded_import
from app.knowledge.kameri.models import HijriMonthContext
from app.knowledge.kameri.repository import get_claim, get_knowledge_base
from app.knowledge.kameri.selector import select_knowledge
assert len(select_knowledge(HijriMonthContext(hijri_month=9)).claims) == 2
assert get_claim('ASMA_NUM_001').application_mode == 'reference_only'
# Once loaded, even a subsequent local read is unnecessary.
__import__('io').open = forbidden
assert len(get_knowledge_base().claims) == 4
assert select_knowledge(HijriMonthContext(hijri_month=1)).abstained
assert not any(name.startswith('app.services') for name in sys.modules)
'''
    # Initialize schema libraries before blocking sockets; the repository has
    # not been imported and no dataset has been read in this fresh process.
    script = 'from app.knowledge.kameri.models import HijriMonthContext\n' + script
    result = subprocess.run([sys.executable, '-c', script], cwd=PACKAGE.parents[2],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
