from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsReadOnlyOrAdmin
from .serializers import (CategorySerializer, GenreSerializer,
                          SignUpSerializer, TitleSerializer,
                          TokenObtainSerializer, UserMeSerializer,
                          UserSerializer)
from .viewsets import CreateListDeleteViewSet
from reviews.models import Category, Genre, Title, User


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

    @action(detail=False, methods=['post'], url_path='signup')
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

    @action(detail=False, methods=['post'], url_path='token')
    def token(self, request):
        """Обработка post-запроса по адресу .../auth/token."""
        serializer = TokenObtainSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            user = User.objects.get(username=username)

            # Генерация JWT-токена
            refresh = RefreshToken.for_user(user)
            return Response({
                'token': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    permission_classes = [permissions.IsAdminUser]
    pagination_class = PageNumberPagination

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
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('name')
    permission_classes = (IsReadOnlyOrAdmin, )


class GenreViewSet(CreateListDeleteViewSet):
    """Вьюсет для просмотра жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsReadOnlyOrAdmin, )


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра произведений."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    filterset_fields = ('category', 'genre', 'name', 'year')
    permission_classes = (IsReadOnlyOrAdmin, )
