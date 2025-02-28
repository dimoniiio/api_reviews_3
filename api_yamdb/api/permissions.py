from rest_framework import permissions


class IsReadOnlyOrAdmin(permissions.BasePermission):
    """Класс для разрешения просмотра объекта любым пользователем.
    Редактировать может только админ.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if (
            request.method == 'PATCH'
            and request.user.is_authenticated
            and request.user.is_admin
        ):
            return True
        return request.user.is_authenticated and (
            request.user.is_admin
        )


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Класс для разрешения просмотра объекта любым пользователем.
    Редактировать может только автор.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class IsAuthorOrModerOrAdminOrReadOnly(permissions.BasePermission):
    """
    Позволяет автору редактировать/удалять объекты,
    остальным только чтение.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            # Разрешить чтение всем
            return True
        # Разрешить изменение только автору, модератору и админу
        return (
            obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        )


class IsAdmin(permissions.BasePermission):
    """Проверяет, является ли пользователь администратором."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsModerator(permissions.BasePermission):
    """Проверяет, является ли пользователь модератором."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_moderator


class IsUser(permissions.BasePermission):
    """Проверяет, является ли пользователь обычным
    аутентифицированным пользователем.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_user
