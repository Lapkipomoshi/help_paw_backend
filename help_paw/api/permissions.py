from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwnerAdminOrReadOnly(BasePermission):
    """Чтение доступно всем, создание зарегистрированным пользователям,
    изменение только владельцу или администратору"""
    def has_permission(self, request, view):
        return (request.method in SAFE_METHODS or
                request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or
                request.user.is_authenticated and
                request.user.id == obj.owner.id or
                request.user.is_admin)


class IsAdminModerOrReadOnly(BasePermission):
    """Чтение доступно всем,
    создание/изменение только администратору или модератору"""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return (request.user.is_authenticated and
                    (request.user.is_admin or
                     request.user.is_moderator))

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or
                request.user.is_authenticated and
                request.user.is_admin or
                request.user.is_moderator)
