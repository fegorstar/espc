from rest_framework.permissions import BasePermission
from .exceptions import CustomException

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
            raise CustomException(
                detail='You do not have permission to perform this action.'
            )

        # Check if the user is a super admin or ADMIN
        if request.user.user_type == 'ADMIN' or request.user.is_superuser:
            return True

        raise CustomException(
            detail='You do not have permission to perform this action.'
        )
