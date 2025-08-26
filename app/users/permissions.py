from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешаем GET, HEAD, OPTIONS запросы всем аутентифицированным
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # Разрешаем все действия только админам
        return request.user.is_authenticated and request.user.role == 'admin'

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Разрешаем доступ админу или владельцу объекта
        return request.user.role == 'admin' or obj == request.user