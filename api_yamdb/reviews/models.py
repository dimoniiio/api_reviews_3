from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

User = get_user_model()
MAX_TEXT_LENGTH = 4096
CHAR_LIMIT = 32
MAX_SCORE_VALUE = 10
MIN_SCORE_VALUE = 1


class Review(models.Model):
    """Класс модели отзыва."""
    text = models.TextField('Текст', max_length=MAX_TEXT_LENGTH)
    author = models.ForeignKey(
        User, verbose_name='Автор публикации',
        on_delete=models.CASCADE, related_name='reviews'
    )
    title = models.IntegerField('Произведение')
    # title = models.ForeignKey(
    #     'Произведение', Title, on_delete=models.SET_NULL, related_name='reviews'
    # )
    score = models.IntegerField(
        'Оценка',
        default=1,
        validators=[
            MaxValueValidator(MAX_SCORE_VALUE),
            MinValueValidator(MIN_SCORE_VALUE)
        ]
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        ordering = ('-pub_date', 'title', 'text',)
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title'), name='unique_review'),
        )

    def __str__(self):
        return self.text[:CHAR_LIMIT]
