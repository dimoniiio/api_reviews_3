from django.core.exceptions import ValidationError
from datetime import date


def validate_year(value):
    """Валидатор для проверки года произведения."""
    current_year = date.today().year
    if value > current_year:
        raise ValidationError(
            'Год выпуска не может быть больше текущего года.',
            code='invalid_year'
        )
