from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import RegexValidator
from rest_framework import serializers, status
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title, User


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для обработки запросов по адресу .../auth/signup."""

    email = serializers.EmailField(
        required=True,
        max_length=settings.MAX_EMAIL_LEN,
    )
    username = serializers.CharField(
        required=True,
        max_length=settings.MAX_USERNAME_LEN,
        validators=[RegexValidator(
            r'^[\w.@+-]+\Z',
            message=('Имя пользователя может содержать только буквы,'
                     'цифры и символы @/./+/-/_.'))]
    )

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

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleReadSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre',
            'category'
        )


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', queryset=Genre.objects.all(), many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre',
            'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отчёта."""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        if self.context.get('request').method == 'POST':
            unique_review = Review.objects.filter(
                author=self.context.get('request').user,
                title_id=self.context.get('view').kwargs.get('title_id')
            )
            if unique_review.exists():
                raise serializers.ValidationError(
                    'Нельзя оставлять более одного отзыва.'
                )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария."""

    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
