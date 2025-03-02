import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers


def validate_username_not_me(value):
    """
    Валидатор, запрещающий использование 'me' в качестве username.
    """
    if value.lower() == 'me':
        raise serializers.ValidationError(
            'Использовать имя "me" в качестве username запрещено.'
        )


def validate_username_characters(value):
    """Функция для проверки недопустимых символов."""
    allowed_pattern = r'^[\w.@+-]+$'

    invalid_characters = re.sub(allowed_pattern, '', value)
    if invalid_characters:
        raise ValidationError(
            _('Недопустимые символы в имени пользователя: %(invalid)s'),
            params={'invalid': ', '.join(set(invalid_characters))},
        )


def username_validator(value):
    """Объединяем обе проверки в один валидатор."""
    validate_username_not_me(value)
    validate_username_characters(value)
