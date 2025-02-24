from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    """Класс описывающий пользователя."""
    ROLE_CHOICES = [
        ('anon', 'Аноним'),
        ('admin', 'Администратор'),
        ('moderator', 'Модератор'),
        ('user', 'Пользователь'),
    ]

    role = models.CharField(
        'Роль',
        max_length=10,
        choices=ROLE_CHOICES,
        default='user'
    )
    bio = models.TextField('Биография', blank=True)
    confirmation_code = models.TextField('Код подтверждения')

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
