from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.conf import settings
from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """Сериалайзер отчёта"""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('author', 'title'),
                message=("Вы уже оставили отзыв.")
            ),
        )

    def validate_score(self, value):
        """Метод валидации рейтинга"""
        if (
            isinstance(value) and 
            settings.MIN_SCORE_VALUE <= value <= settings.MAX_SCORE_VALUE
        ):
            return value
        raise serializers.ValidationError(
            'Оценка должена быть в диапозоне '
            f'от {settings.MIN_SCORE_VALUE} до {settings.MAX_SCORE_VALUE}.')

    def validate_text(self, value):
        """Метод валидации текста отзыва."""
        if len(value) > settings.MAX_TEXT_LENGTH:
            return value
        raise serializers.ValidationError(
            'Максимальное количество символов в отзыве: '
            f'{settings.MAX_TEXT_LENGTH}.'
        )
