from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import ADMIN, MODERATOR, USER


class API_User(AbstractUser):
    """Класс описывающий пользователя."""

    class Role(models.TextChoices):
        USER = USER, 'Пользователь'
        MODERATOR = MODERATOR, 'Модератор'
        ADMIN = ADMIN, 'Администратор'

    email = models.EmailField(unique=True)
    role = models.CharField(
        'Роль',
        max_length=max(len(role) for role, _ in Role.choices),
        choices=Role.choices,
        default=Role.USER
    )
    bio = models.TextField('Биография', blank=True)

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    def __str__(self):
        return f"{self.username} ({self.role})"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username', 'email']
