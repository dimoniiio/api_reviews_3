from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import IsAuthorOrReadOnly, IsReadOnlyOrAdmin
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, SignUpSerializer,
                          TitleSerializer, TokenObtainSerializer,
                          UserMeSerializer)
from .viewsets import CreateListDeleteViewSet
from reviews.models import Category, Genre, Review, Title, User


class AuthViewSet(viewsets.ViewSet):
    """Регистрация новых польщователей и редактирование профиля."""

    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
        """Обработка post-запроса по адресу .../auth/signup."""
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']

            # Создание пользователя
            user, created = User.objects.get_or_create(
                username=username, email=email)
            if created:
                # Генерация confirmation_code
                confirmation_code = default_token_generator.make_token(user)
                user.confirmation_code = confirmation_code
                user.save()

                # Отправка письма с кодом подтверждения
                send_mail(
                    subject='Код подтверждения YaMDB',
                    message=f'Ваш код подтверждения: {confirmation_code}',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )

                return Response({'email': email, 'username': username},
                                status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Пользователь уже существует.'},
                                status=status.HTTP_400_BAD_REQUEST)
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

    @action(detail=False, methods=['patch'], url_path='me')
    def me(self, request):
        """Обработка patch-запроса по адресу .../auth/me."""
        user = request.user
        serializer = UserMeSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class ReviewViewSet(viewsets.ModelViewSet):
    """Предсталение отзыва на произведение."""

    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly,)

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


class CommentViewSet(viewsets.ModelViewSet):
    """Предсталение комментария к отзыву."""

    serializer_class = CommentSerializer
    pagination_class = PageNumberPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsAuthorOrReadOnly,)

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
        return self.commented_review.reviews.all()

    def perform_create(self, serializer):
        """Метод переопределения автора и произведения у отзыва."""
        serializer.save(
            author=self.request.user,
            review=self.commented_review
        )
