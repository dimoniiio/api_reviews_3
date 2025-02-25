from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import (
    MAX_SCORE_VALUE, MAX_TEXT_LENGTH, MIN_SCORE_VALUE, Review
)


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
        if isinstance(value) and MIN_SCORE_VALUE <= value <= MAX_SCORE_VALUE:
            return value
        raise serializers.ValidationError(
            f'Оценка должена быть в диапозоне '
            f'от {MIN_SCORE_VALUE} до {MAX_SCORE_VALUE}.')

    def validate_text(self, value):
        """Метод валидации текста отзыва."""
        if len(value) > MAX_TEXT_LENGTH:
            return value
        raise serializers.ValidationError(
            f'Максимальное количество символов в отзыве: {MAX_TEXT_LENGTH}.')
