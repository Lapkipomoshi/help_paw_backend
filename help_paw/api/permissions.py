from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminModerOrReadOnly(BasePermission):
    """Чтение доступно всем,
    создание/изменение только администратору или модератору"""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        else:
            return (request.user.is_authenticated and
                    (request.user.is_admin or request.user.is_moderator))


class AuthenticatedAllowToPost(BasePermission):
    def has_permission(self, request, view):
        return request.method == 'POST' and request.user.is_authenticated


class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.author


class IsShelterOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_shelter_owner
