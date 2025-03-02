from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.relations import SlugRelatedField

from users.validators import username_validator
from reviews.models import Category, Comment, Genre, Review, Title
from users.constants import MAX_EMAIL_LEN, MAX_USERNAME_LEN

User = get_user_model()


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для обработки запросов по адресу .../auth/signup."""

    email = serializers.EmailField(
        required=True,
        max_length=MAX_EMAIL_LEN,
    )
    username = serializers.CharField(
        required=True,
        max_length=MAX_USERNAME_LEN,
        validators=[username_validator]
    )

    def validate(self, data):
        """Проверка данных: username и email."""
        username = data.get('username')
        email = data.get('email')

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

    def create(self, validated_data):
        """Метод для создания пользователя и отправки кода подтверждения."""
        username = validated_data['username']
        email = validated_data['email']

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        confirmation_code = default_token_generator.make_token(user)

        self.send_email_token(
            text='Код подтверждения YaMDB',
            confirmation_code=confirmation_code,
            email=email
        )

        return user

    def send_email_token(self, text, confirmation_code, email):
        """Отправка сообщения на почту с кодом подтверждения."""
        send_mail(
            subject=text,
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для обработки запросов по адресу .../auth/token."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        """Проверка данных: username и confirmation_code."""
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        try:
            user = get_object_or_404(User, username=username)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                {'username': 'Пользователь с таким именем не существует.'},
                code=status.HTTP_404_NOT_FOUND
            )

        if not default_token_generator.check_token(user, confirmation_code):
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


class UserMeSerializer(UserSerializer):
    """Сериализатор модели User для пользователя"""

    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)


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
        allow_null=False, allow_empty=False,
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
