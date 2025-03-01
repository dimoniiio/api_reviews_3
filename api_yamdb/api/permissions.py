from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """Класс для разрешения просмотра объекта любым пользователем.
    Редактировать может только админ.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_admin
        )


class IsAuthorOrModerOrAdminOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Позволяет автору, модератору или администратору
    редактировать/удалять объекты,
    а всем остальным пользователям — только чтение.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        )


class IsAdmin(permissions.BasePermission):
    """Проверяет, является ли пользователь администратором."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
