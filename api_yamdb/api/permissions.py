from rest_framework import permissions


class IsReadOnlyOrAdmin(permissions.BasePermission):
    """Класс для разрешения просмотра объекта любым пользователем.
    Редактировать может только админ.
    """

    def has_permission(self, request, view):
        return bool(
            (request.method in permissions.SAFE_METHODS)
            or (request.user.is_staff or request.user.is_superuser)
        )

    # def has_object_permission(self, request, view, obj):
    #     return bool(
    #         (request.method in permissions.SAFE_METHODS)
    #         or (request.user.is_staff)
    #     )


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Класс для разрешения просмотра объекта любым пользователем.
    Редактировать может только автор.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
