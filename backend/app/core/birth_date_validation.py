from datetime import date


def validate_birth_date(value: date, *, today: date) -> date:
    """Shared admission rule; callers explicitly supply the validation date."""
    if value > today:
        raise ValueError("Doğum tarihi gelecekte olamaz.")
    return value
