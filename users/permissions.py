from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Admin uniquement"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "admin"
        )


class IsCommercial(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "commercial"
        )


class IsAssistant(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "assistant"
        )


class IsAnalyst(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "analyst"
        )


class IsManager(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == "manager"
        )


class IsAdminOrManager(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ["admin", "manager"]
        )


class IsAdminOrSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.role == "admin" or
            obj == request.user
        )