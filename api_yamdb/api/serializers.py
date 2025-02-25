from rest_framework import serializers

from reviews.models import User


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
