from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator


User = get_user_model()


class Title(models.Model):
    name = models.CharField('Название произведения', max_length=256)
    category = models.ForeignKey(
        'Category',
        on_delete=models.DO_NOTHING,
        related_name='titles',
        verbose_name='Категория'
    )
    # genre = models.ManyToManyField(
    #     'Genre',
    #     through='GenreTitle',
    #     related_name='titles',
    #     verbose_name='Жанр'
    # )
    genre = models.IntegerField()
    year = models.IntegerField('Год произведения',)
    description = models.TextField('Описание произведения', blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField('Название категории', max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField('Название жанра', max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    """Класс модели отзыва."""

    text = models.TextField('Текст', max_length=settings.MAX_TEXT_LENGTH)
    author = models.ForeignKey(
        User, verbose_name='Автор публикации',
        on_delete=models.CASCADE, related_name='reviews'
    )
    title = models.ForeignKey(
        'Произведение', Title, 
        on_delete=models.SET_NULL, related_name='reviews'
    )
    score = models.IntegerField(
        'Оценка',
        default=1,
        validators=[
            MaxValueValidator(settings.MAX_SCORE_VALUE),
            MinValueValidator(settings.MIN_SCORE_VALUE)
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
        return self.text[:settings.CHAR_LIMIT]
