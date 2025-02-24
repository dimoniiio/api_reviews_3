from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import User
from .serializers import (SignUpSerializer, TokenObtainSerializer,
                          UserMeSerializer)


class AuthViewSet(viewsets.ViewSet):
    """Регистрация новых польщователей и редактирование профиля."""

    @action(detail=False, methods=['post'], url_path='signup')
    def signup(self, request):
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
        user = request.user
        serializer = UserMeSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
