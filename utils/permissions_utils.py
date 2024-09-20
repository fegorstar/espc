from rest_framework.permissions import BasePermission
from rest_framework import status



def generate_verification_code():
    return str(random.randint(10000, 99999))


class IsUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_active
            and (request.user.user_type in ['PATIENT', 'ADMIN'])
        )

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_active
            and request.user.user_type == 'ADMIN'
        )


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.user_type == 'ADMIN' or request.user.is_superuser:
            return True

        return False
