from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ErrorDetail
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .filters import TitleFilter
from .pagination import CustomPageNumberPagination
from .permissions import (IsAdmin, IsAuthorOrModerOrAdminOrReadOnly,
<<<<<<< HEAD
                          IsReadOnlyOrAdmin)
=======
                          IsAuthorOrReadOnly, IsModerator, IsAdminOrReadOnly,
                          IsUser)
>>>>>>> fix_our_review
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          TokenObtainSerializer,
                          UserMeSerializer, UserSerializer)
from .viewsets import CreateListDeleteViewSet
from reviews.models import Category, Genre, Review, Title, User


class AuthViewSet(viewsets.ViewSet):
    """Регистрация новых пользователей и редактирование профиля."""

    def send_email_token(self, text, confirmation_code, email):
        """Отправка сообщения на почту."""
        send_mail(
            subject=text,
            message=f'Ваш код подтверждения: {confirmation_code}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )

    @action(detail=False,
            methods=['post'],
            url_path='signup',
            authentication_classes=[],
            permission_classes=[])
    def signup(self, request):
        """Обработка post-запроса по адресу .../auth/signup."""
        serializer = SignUpSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']

            # Попытка получить или создать пользователя
            user, created = User.objects.get_or_create(
                username=username, email=email)

            if created:
                # Для нового пользователя: генерация confirmation_code
                confirmation_code = default_token_generator.make_token(user)
                user.confirmation_code = confirmation_code
                user.save()
                # Отправка письма с кодом подтверждения
                self.send_email_token(text='Код подтверждения YaMDB',
                                      confirmation_code=confirmation_code,
                                      email=email)
                return Response(
                    {'email': email, 'username': username},
                    status=status.HTTP_200_OK)

            else:
                # Для существующего пользователя: обновление confirmation_code
                confirmation_code = default_token_generator.make_token(user)
                user.confirmation_code = confirmation_code
                user.save()
                # Отправка нового кода подтверждения
                self.send_email_token(text='Новый код подтверждения YaMDB',
                                      confirmation_code=confirmation_code,
                                      email=email)
                return Response(
                    {'detail': 'Код подтверждения отправлен повторно.'},
                    status=status.HTTP_200_OK)

        # Возвращаем ошибки сериализатора, если данные некорректны
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['post'],
            url_path='token',
            authentication_classes=[],
            permission_classes=[])
    def token(self, request):
        """Обработка post-запроса по адресу .../auth/token."""

        STATUS_CODES = {
            200: status.HTTP_200_OK,
            400: status.HTTP_400_BAD_REQUEST,
            404: status.HTTP_404_NOT_FOUND,
            500: status.HTTP_500_INTERNAL_SERVER_ERROR,
        }

        serializer = TokenObtainSerializer(data=request.data)

        if not serializer.is_valid():
            # Извлекаем статус-код из ValidationError
            errors = serializer.errors
            status_code = status.HTTP_400_BAD_REQUEST  # Значение по умолчанию

            # Проверяем presence of custom status code in ValidationError
            for field_errors in errors.values():
                for error in field_errors:
                    if isinstance(error, ErrorDetail) and hasattr(error,
                                                                  'code'):
                        status_code = STATUS_CODES.get(
                            error.code,
                            status.HTTP_400_BAD_REQUEST)
                        break

            return Response(errors, status=status_code)

        user = serializer.validated_data['user']

        # Генерация JWT-токена
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token)
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

    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def update(self, request, *args, **kwargs):
        """Запрещаем использование PUT-запроса."""
        if request.method == 'PUT':
            return Response(
                {'detail': 'Метод PUT не поддерживается.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        """Список всех пользователей."""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Создание нового пользователя."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def retrieve(self, request, *args, **kwargs):
        """Получение данных о конкретном пользователе по username."""
        instance = self.get_object()  # Получаем пользователя по username
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Удаление пользователя."""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
        elif request.method == 'PATCH':
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
    pagination_class = CustomPageNumberPagination
    filterset_class = TitleFilter
    permission_classes = (IsAdminOrReadOnly, )

    def http_method_not_allowed(self, request, *args, **kwargs):
        if request.method == 'PUT':
            raise MethodNotAllowed(request.method)
        return super().http_method_not_allowed(request, *args, **kwargs)

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
