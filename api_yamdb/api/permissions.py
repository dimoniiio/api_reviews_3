from rest_framework import permissions


class IsReadOnlyOrAdmin(permissions.IsAuthenticatedOrReadOnly):

    def has_object_permission(self, request, view, obj):
        print(obj)
        print(dir(obj))
        return bool(
            (request.method in permissions.SAFE_METHODS)
            or (obj.author is request.is_staff)
        )
