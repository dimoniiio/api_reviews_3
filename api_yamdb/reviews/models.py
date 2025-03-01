import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import MAX_LENGTH_NAME, MAX_LENGTH_SLUG

User = get_user_model()


class NameAndSlugAbstractModel(models.Model):
    """Абстрактный класс для наследования полей названия и слага."""

    name = models.CharField(
        'Название категории',
        max_length=MAX_LENGTH_NAME
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_SLUG,
        unique=True
    )

    class Meta:
        abstract = True
        ordering = ('slug',)

    def __str__(self):
        return self.name


class Category(NameAndSlugAbstractModel):
    """Класс модели категория."""

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(NameAndSlugAbstractModel):
    """Класс модели жанр."""

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class GenreTitle(models.Model):
    title = models.ForeignKey(
        'Title',
        on_delete=models.SET_NULL,
        null=True
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        null=True
    )


class Title(models.Model):
    """Класс модели произведения."""

    name = models.CharField(
        'Название произведения',
        max_length=MAX_LENGTH_NAME
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        through=GenreTitle,
        related_name='titles',
        verbose_name='Жанр'
    )
    year = models.PositiveSmallIntegerField('Год произведения',)
    description = models.TextField('Описание произведения', blank=True)

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def clean(self):
        now_year = datetime.date.today().year # ПРОВЕРИТЬ РАБОТАЕТ ЛИ?
        if self.year > now_year:
            raise ValidationError(
                'Год выпуска не может быть больше текущего года.'
            )

    def __str__(self):
        return self.name


class Review(models.Model):
    """Класс модели отзыв."""

    text = models.TextField('Текст', max_length=settings.MAX_REVIEW_LENGTH)
    author = models.ForeignKey(
        User, verbose_name='Автор',
        on_delete=models.CASCADE, related_name='reviews'
    )
    title = models.ForeignKey(
        Title, verbose_name='Произведение',
        on_delete=models.CASCADE, related_name='reviews'
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
        unique_together = ['author', 'title']

    def __str__(self):
        return self.text[:settings.CHAR_LIMIT]


class Comment(models.Model):
    """Класс модели комментарий."""

    text = models.TextField('Текст', max_length=settings.MAX_COMMENT_LENGTH)
    review = models.ForeignKey(
        Review, verbose_name='Отзыв',
        on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        User, verbose_name='Автор',
        on_delete=models.CASCADE, related_name='comments'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
        ordering = ('pub_date', 'review', 'text',)

    def __str__(self):
        return self.text[:settings.CHAR_LIMIT]
