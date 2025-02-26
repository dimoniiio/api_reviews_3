import datetime

from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Category, Genre, Title, User


class SignUpSerializer(serializers.Serializer):
    """Сериализатор для обработки запросов по адресу .../auth/signup."""

    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError(
                "Пользователь с таким username уже существует.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует.")
        return data


class TokenObtainSerializer(serializers.Serializer):
    """Сериализатор для обработки запросов по адресу .../auth/token."""

    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        user = User.objects.filter(username=data['username']).first()
        if not user or user.confirmation_code != data['confirmation_code']:
            raise serializers.ValidationError(
                "Неверный username или код подтверждения.")
        return data


class UserMeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'bio')
        read_only_fields = ('username', 'email', 'role')


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

    # def get_rating(self, obj):
    #     reviews = Review.objects.filter(title=obj)
    #     if reviews.exists():
    #         average_score = reviews.aggregate(Avg('score'))['score__avg']
    #         return round(average_score, 1)
    #     return None
