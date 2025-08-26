from rest_framework import permissions


class IsAuthorOrExecutorOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Админ может всё
        if request.user.role == "admin":
            return True
        # Автор задачи может её редактировать и удалять
        if request.method in ["PUT", "PATCH", "DELETE"] and obj.author == request.user:
            return True
        # Исполнитель может менять статус (PATCH)
        if request.method == "PATCH" and obj.executor == request.user:
            return True
        # Все аутентифицированные могут видеть задачу (GET)
        return request.method in permissions.SAFE_METHODS
