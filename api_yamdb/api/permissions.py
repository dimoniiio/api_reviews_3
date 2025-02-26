from rest_framework import permissions


class IsReadOnlyOrAdmin(permissions.IsAuthenticatedOrReadOnly):
    """Класс для разрешения просмотра объекта любым пользователем.
    Редактировать может только админ.
    """

    def has_object_permission(self, request, view, obj):
        return bool(
            (request.method in permissions.SAFE_METHODS)
            or (obj.author is request.is_staff)
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
