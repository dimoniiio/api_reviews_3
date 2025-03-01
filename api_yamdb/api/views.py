from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ErrorDetail, MethodNotAllowed
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from .pagination import CustomPageNumberPagination
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAuthorOrModerOrAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          TokenObtainSerializer, UserMeSerializer,
                          UserSerializer)
from .viewsets import CreateListDeleteViewSet
from reviews.models import Category, Genre, Review, Title, User


class AuthViewSet(viewsets.ViewSet):
    """Регистрация новых пользователей и редактирование профиля."""

    @action(detail=False,
            methods=['post'],
            url_path='signup',
            authentication_classes=[],
            permission_classes=[])
    def signup(self, request):
        """Обработка post-запроса по адресу .../auth/signup."""
        serializer = SignUpSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {'email': user.email, 'username': user.username},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['post'],
            url_path='token',
            authentication_classes=[],
            permission_classes=[])
    def token(self, request):
        """Обработка post-запроса по адресу .../auth/token."""

        serializer = TokenObtainSerializer(data=request.data)

        if not serializer.is_valid(raise_exception=True):
            pass

        user = serializer.validated_data['user']

        # Генерация JWT-токена
        access_token = AccessToken.for_user(user)
        return Response({
            'token': str(access_token)
        }, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с пользователями.
    Администратор может:

    GET: Получить список всех пользователей.
    POST: Создать нового пользователя.
    PATCH Изменить данные пользователя.
    DELETE: Удалить пользователя.

    Любой авторизованный пользователь может:
    GET: Получить свои данные (/me/).
    PATCH: Изменить свои данные (/me/).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    pagination_class = CustomPageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    lookup_field = 'username'

    http_method_names = ['get', 'post', 'patch', 'delete',]

    @action(detail=False,
            methods=['get', 'patch'],
            permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        """
        Получение или изменение данных текущего пользователя.
        GET: Получить данные текущего пользователя.
        PATCH: Изменить данные текущего пользователя.
        """
        user = request.user
        if request.method == 'GET':
            serializer = UserMeSerializer(user)
            return Response(serializer.data)
        else:
            serializer = UserMeSerializer(user,
                                          data=request.data,
                                          partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class CategoryViewSet(CreateListDeleteViewSet):
    """Вьюсет для просмотра категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(CreateListDeleteViewSet):
    """Вьюсет для просмотра жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра произведений."""

    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    )
    pagination_class = PageNumberPagination
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly, )
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Предсталение отзыва на произведение."""

    serializer_class = ReviewSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrModerOrAdminOrReadOnly,)

    @property
    def reviewed_title(self):
        """Метод получения объекта класса произведение по id."""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Метод получения всех отзывов к произведению."""
        return self.reviewed_title.reviews.all()

    def perform_create(self, serializer):
        """Метод переопределения автора и произведения у отзыва."""
        serializer.save(author=self.request.user, title=self.reviewed_title)

    def update(self, request, *args, **kwargs):
        if self.request.method == 'PUT':
            return Response({'detail': 'Метод PUT не поддерживается.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    """Предсталение комментария к отзыву."""

    serializer_class = CommentSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrModerOrAdminOrReadOnly,)

    @property
    def reviewed_title(self):
        """Метод получения объекта класса произведение по id."""
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    @property
    def commented_review(self):
        """Метод получения объекта класса отзыва по id."""
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        if review.title == self.reviewed_title:
            return review
        raise Http404

    def get_queryset(self):
        """Метод получения всех комметариев к отзыву."""
        return self.commented_review.comments.all()

    def perform_create(self, serializer):
        """Метод переопределения автора и отзыва у коментария."""
        serializer.save(
            author=self.request.user,
            review=self.commented_review
        )

    def update(self, request, *args, **kwargs):
        if self.request.method == 'PUT':
            return Response({'detail': 'Метод PUT не поддерживается.'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)
