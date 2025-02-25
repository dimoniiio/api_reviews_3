import datetime

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Title, Category, Genre, Comment, Review


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    genre = SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='name', many=True
    )
    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name'
    )
    rating = serializers.IntegerField(
        required=False,
        read_only=True,
        default=None
    )

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


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'pub_date')
