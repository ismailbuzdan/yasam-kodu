"""Pure project-specific Pythagorean convention. No clock, I/O or interpretation."""
import unicodedata

from app.schemas.numerology import NumerologyMetadata, NumerologyNumber, NumerologyRequest, NumerologyResponse

MASTER_NUMBERS = (11, 22, 33)
LETTER_VALUES = {letter: value for value, letters in enumerate(
    ("AJS", "BKT", "CLU", "DMV", "ENW", "FOX", "GPY", "HQZ", "IR"), start=1)
    for letter in letters}
VOWELS = "AEIOU"
TURKISH_LETTERS = str.maketrans("ÇçĞğİıÖöŞşÜü", "CcGgIiOoSsUu")


class NumerologyError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)


def normalize_name(name: str) -> str:
    # NFC accepts decomposed Turkish letters without transliterating other alphabets.
    # Check original letters first: NFC must not silently turn e.g. Kelvin sign into K.
    for char in name:
        if unicodedata.category(char).startswith("L") and not (
            char.isascii() or ord(char) in TURKISH_LETTERS
        ):
            raise NumerologyError("unsupported_name_characters", "Ad yalnız Latin A-Z ve Türkçe harfler içerebilir.")
    letters = []
    for char in unicodedata.normalize("NFC", name).translate(TURKISH_LETTERS):
        if char.isascii() and char.isalpha():
            letters.append(char.upper())
        elif char.isspace() or unicodedata.category(char).startswith(("P", "Z")):
            continue
        elif unicodedata.category(char).startswith(("L", "M")):
            raise NumerologyError("unsupported_name_characters", "Ad yalnız Latin A-Z ve Türkçe harfler içerebilir.")
        else:
            raise NumerologyError("invalid_name", "Ad rakam veya sembol içeremez.")
    if not letters:
        raise NumerologyError("invalid_name", "En az bir desteklenen harf içeren ad girin.")
    return "".join(letters)


def digit_sum(number: int) -> int:
    return sum(int(digit) for digit in str(number))


def reduce_core_number(number: int) -> int:
    if number < 1:
        raise ValueError("A positive number is required.")
    while number > 9 and number not in MASTER_NUMBERS:
        number = digit_sum(number)
    return number


def reduce_to_single_digit(number: int) -> int:
    if number < 1:
        raise ValueError("A positive number is required.")
    while number > 9:
        number = digit_sum(number)
    return number


def number_result(raw: int, *, preserve_master: bool = True) -> NumerologyNumber:
    value = reduce_core_number(raw) if preserve_master else reduce_to_single_digit(raw)
    return NumerologyNumber(raw_sum=raw, value=value, is_master=value in MASTER_NUMBERS)


class NumerologyService:
    def calculate(self, request: NumerologyRequest) -> NumerologyResponse:
        name = normalize_name(request.full_name)
        vowel_sum = sum(LETTER_VALUES[c] for c in name if c in VOWELS)
        consonant_sum = sum(LETTER_VALUES[c] for c in name if c not in VOWELS)
        birth = request.birth_date
        life_path = number_result(digit_sum(birth.year) + digit_sum(birth.month) + digit_sum(birth.day))
        expression = number_result(vowel_sum + consonant_sum)
        personal_year = None
        if request.target_year is not None:
            personal_year = number_result(digit_sum(birth.month) + digit_sum(birth.day)
                                          + digit_sum(request.target_year), preserve_master=False)
        return NumerologyResponse(
            metadata=NumerologyMetadata(master_numbers=MASTER_NUMBERS, target_year=request.target_year),
            life_path=life_path, birthday=number_result(birth.day), expression=expression,
            soul_urge=number_result(vowel_sum) if vowel_sum else None,
            personality=number_result(consonant_sum) if consonant_sum else None,
            maturity=number_result(life_path.value + expression.value), personal_year=personal_year)
