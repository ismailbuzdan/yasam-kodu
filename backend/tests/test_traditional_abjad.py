from dataclasses import FrozenInstanceError, asdict
import unicodedata

import pytest

from app.services.traditional.abjad import calculate_abjad
from app.services.traditional.models import TraditionalError

# Hand-derived from K0's explicitly selected factual table, not imported mapping.
VECTORS = [('ا',1),('ب',2),('ج',3),('د',4),('ه',5),('و',6),('ز',7),('ح',8),('ط',9),
    ('ي',10),('ك',20),('ل',30),('م',40),('ن',50),('س',60),('ع',70),('ف',80),('ص',90),
    ('ق',100),('ر',200),('ش',300),('ت',400),('ث',500),('خ',600),('ذ',700),('ض',800),
    ('ظ',900),('غ',1000),('ة',400),('ى',10),('أ',1),('إ',1),('آ',1),('ؤ',1),('ئ',1),
    ('ء',1),('ٱ',1),('پ',2),('چ',3),('ژ',7),('ڭ',20),('ک',20),('ی',10),('گ',20),
    ('ابج',6),('ؤئء',3),('پچژڭ',32),('بّ',2)]


@pytest.mark.parametrize('text,expected', VECTORS)
def test_factual_values_and_canonical_equivalents(text, expected):
    assert calculate_abjad(text, confirmed=True).raw_sum == expected
    assert calculate_abjad(unicodedata.normalize('NFD', text), confirmed=True).raw_sum == expected


@pytest.mark.parametrize('codepoint', range(0xFEF5, 0xFEFD))
def test_only_eight_lam_alif_ligatures(codepoint):
    assert calculate_abjad(chr(codepoint), confirmed=True).raw_sum == 31


@pytest.mark.parametrize('ignored', [chr(c) for c in range(0x064B, 0x0653)] +
    list('\u0670\u0640\t\n\r \u00a0\u0027,-.\u2019\u060c\u061b\u061f'))
def test_exact_ignored_allowlist(ignored):
    assert calculate_abjad('ب' + ignored, confirmed=True).raw_sum == 2


@pytest.mark.parametrize('bad', list('A0١۱😀\u200c\u200d\u202e\u2066\u061cڤٹۀ\u0653\u0654\u0655\u0656\u06d6:!_\v\f\u2002\ufdf2\ufe8f'))
def test_reject_whole_input_without_echo(bad, caplog):
    submitted = 'ابج' + bad + 'غ'
    with pytest.raises(TraditionalError) as error:
        calculate_abjad(submitted, confirmed=True)
    assert error.value.code == 'unsupported_abjad_character'
    assert submitted not in str(error.value) + repr(error.value) + caplog.text
    assert error.value.__cause__ is None


@pytest.mark.parametrize('text', ['', ' ,-', '\t\n\u0640\u0651', None, 123])
def test_requires_counted_letter(text):
    with pytest.raises(TraditionalError, match='invalid_abjad_text'):
        calculate_abjad(text, confirmed=True)


@pytest.mark.parametrize('confirmed', [False, None, 1, 'true'])
def test_requires_explicit_confirmation(confirmed):
    with pytest.raises(TraditionalError, match='invalid_abjad_text'):
        calculate_abjad('ابج', confirmed=confirmed)


def test_result_privacy_and_frozen(caplog):
    result = calculate_abjad('ابج', confirmed=True)
    assert 'ابج' not in repr(result) + repr(asdict(result)) + caplog.text
    assert not any(key in asdict(result) for key in ('text', 'normalized_text', 'letters'))
    with pytest.raises(FrozenInstanceError):
        result.raw_sum = 0


def test_all_other_arabic_presentation_forms_are_rejected():
    for codepoint in list(range(0xFB50, 0xFE00)) + list(range(0xFE70, 0xFF00)):
        if 0xFEF5 <= codepoint <= 0xFEFC:
            continue
        with pytest.raises(TraditionalError, match='unsupported_abjad_character'):
            calculate_abjad(chr(codepoint), confirmed=True)
