from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import date


def validate_year(value):
    """Валидатор для проверки года произведения."""
    current_year = date.today().year
    if value > current_year:
        raise ValidationError(
            _('Год выпуска не может быть больше текущего года.'),
            code='invalid_year'
        )