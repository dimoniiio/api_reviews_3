import datetime

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg
from rest_framework import serializers, status
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title, User


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для обработки запросов по адресу .../auth/signup."""

    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    def validate(self, data):
        """Проверка данных: username и email."""
        username = data.get('username')
        email = data.get('email')

        if username == 'me':
            raise serializers.ValidationError(
                {'username':
                 'Использовать имя "me" в качестве username запрещено.'},
                code=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(username=username
                               ).exclude(email=email).exists():
            raise serializers.ValidationError(
                {'username': 'Это имя пользователя уже занято.'},
                code=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(email=email
                               ).exclude(username=username).exists():
            raise serializers.ValidationError(
                {'email': 'Этот email уже используется.'},
                code=status.HTTP_400_BAD_REQUEST
            )

        return data


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для обработки запросов по адресу .../auth/token."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        """Проверка данных: username и confirmation_code."""
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        if not username:
            raise serializers.ValidationError(
                {'username': 'Это поле является обязательным.'},
                code=status.HTTP_400_BAD_REQUEST
            )
        if not confirmation_code:
            raise serializers.ValidationError(
                {'confirmation_code': 'Это поле является обязательным.'},
                code=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                {'username': 'Пользователь с таким именем не существует.'},
                code=status.HTTP_404_NOT_FOUND
            )

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                {'confirmation_code': 'Неверный код подтверждения.'},
                code=status.HTTP_400_BAD_REQUEST
            )

        data['user'] = user
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User для админа."""
    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role')
        extra_kwargs = {
            'role': {'required': False},
            'bio': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False},
        }

    def validate_username(self, value):
        """Проверка, что username не может быть 'me'."""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                "Имя пользователя 'me' запрещено.")
        return value


class UserMeSerializer(UserSerializer):
    """Сериализатор модели User для пользователя"""

    role = serializers.CharField(read_only=True)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров."""

    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(queryset=Genre.objects.all())]
    )

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    slug = serializers.SlugField(
        max_length=50,
        validators=[UniqueValidator(queryset=Category.objects.all())]
    )

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для произведений."""

    genre = SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='name', many=True
    )
    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name'
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')

    def validate_year(self, value):
        now_year = datetime.date.today().year
        if value > now_year:
            raise serializers.ValidationError(
                'Год выпуска не может быть больше текущего года.'
            )
        return value

    def get_rating(self, obj):
        reviews = Review.objects.filter(title=obj)
        if reviews.exists():
            average_score = reviews.aggregate(Avg('score'))['score__avg']
            return round(average_score, 1)
        return None


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отчёта."""

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
            isinstance(value)
            and settings.MIN_SCORE_VALUE <= value <= settings.MAX_SCORE_VALUE
        ):
            return value
        raise serializers.ValidationError(
            'Оценка должена быть в диапозоне '
            f'от {settings.MIN_SCORE_VALUE} до {settings.MAX_SCORE_VALUE}.')

    def validate_text(self, value):
        """Метод валидации текста отзыва."""
        if len(value) > settings.MAX_REVIEW_LENGTH:
            return value
        raise serializers.ValidationError(
            'Максимальное количество символов в отзыве: '
            f'{settings.MAX_REVIEW_LENGTH}.'
        )


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария."""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
