from django.db import models
from django.core.validators import MaxValueValidator
from django.contrib.auth import get_user_model


User = get_user_model()


class Title(models.Model):
    name = models.CharField('Название произведения', max_length=256)
    category = models.ForeignKey(
        'Category',
        on_delete=models.DO_NOTHING,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        'Genre',
        through='GenreTitle',
        related_name='titles',
        verbose_name='Жанр'
    )
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
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        blank=True,
        null=True,
        verbose_name='Произведение'
    )
    text = models.TextField('Текст отзыва')
    score = models.PositiveIntegerField(
        'Оценка произведения',
        validators=[MaxValueValidator(10)],
    )
    pub_date = models.DateTimeField('Дата отзыва', auto_now_add=True)


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField('Текст комментария')
    pub_date = models.DateTimeField('Дата комментария', auto_now_add=True)
    Review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )


class GenreTitle(models.Model):
    title = models.ForeignKey(Title, on_delete=models.DO_NOTHING)
    genre = models.ForeignKey(Genre, on_delete=models.DO_NOTHING)
