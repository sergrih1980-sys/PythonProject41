from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение на редактирование объекта только его владельцу.
    Безопасно (GET, HEAD, OPTIONS) — всем.
    Изменение (PUT, PATCH, DELETE) — только владельцу.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user