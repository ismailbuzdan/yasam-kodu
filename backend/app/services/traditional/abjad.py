"""Confirmed-script additive abjad. Tables independently encoded from K0."""
from unicodedata import normalize, unidata_version

from .models import AbjadResult, TraditionalError

_VALUES = dict(zip('ابجدهوزحطيكلمنسعفصقرشتثخذضظغ',
    (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90,
     100, 200, 300, 400, 500, 600, 700, 800, 900, 1000), strict=True))
_VALUES.update({'ة': 400, 'ى': 10, 'أ': 1, 'إ': 1, 'آ': 1, 'ؤ': 1, 'ئ': 1,
    'ء': 1, 'ٱ': 1, 'پ': 2, 'چ': 3, 'ژ': 7, 'ڭ': 20, 'ک': 20, 'ی': 10, 'گ': 20})
_LIGATURES = dict(zip(range(0xFEF5, 0xFEFD),
                     ('لآ', 'لآ', 'لأ', 'لأ', 'لإ', 'لإ', 'لا', 'لا'), strict=True))
_IGNORED = frozenset(chr(c) for c in range(0x064B, 0x0653)) | frozenset(
    '\u0670\u0640\t\n\r \u00a0\u0027,-.\u2019\u060c\u061b\u061f')


def calculate_abjad(text: str, *, confirmed: bool) -> AbjadResult:
    """Confirmation applies to this exact input and abjad_text_v1 policy.

    Caller must obtain renewed confirmation after edits/policy changes. No input
    object, normalized string, or per-letter trace is retained in output/errors.
    """
    if confirmed is not True or not isinstance(text, str) or not text:
        raise TraditionalError('invalid_abjad_text')
    normalized = normalize('NFC', normalize('NFC', text).translate(_LIGATURES))
    total = 0
    for character in normalized:
        if character in _VALUES:
            total += _VALUES[character]
        elif character not in _IGNORED:
            raise TraditionalError('unsupported_abjad_character')
    if total == 0:
        raise TraditionalError('invalid_abjad_text')
    return AbjadResult(total, unidata_version)
