from rest_framework import serializers


def validate_username_not_me(value):
    """
    Валидатор, запрещающий использование 'me' в качестве username.
    """
    if value.lower() == 'me':
        raise serializers.ValidationError(
            'Использовать имя "me" в качестве username запрещено.'
        )
