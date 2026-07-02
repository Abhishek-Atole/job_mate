from rest_framework import permissions


class IsEmployer(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'employer'


class IsCandidate(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'candidate'


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'admin'


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(obj, 'employer'):
            return obj.employer.user == request.user
        return obj.user == request.user
