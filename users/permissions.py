from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from users.models import User

class StaffPermissions(permissions.BasePermission):
    """
    Permissions for staff.
    """
    def has_permission(self, request, view):
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to access this.")
        return True
    
class CustomerPermissions(permissions.BasePermission):
    """
    Permissions for customers only.
    """
    def has_permission(self, request, view):
        if not request.user.role == User.Role.CUSTOMER:
            raise PermissionDenied("Please log in as a customer.")
        return True
    
class ManagerPermissions(permissions.BasePermission):
    """
    Permissions for managers only.
    """
    def has_permission(self, request, view):
        if not request.user.role == User.Role.MANAGER:
            raise PermissionDenied("Please log in as a manager.")
        return True
    
class IsAuthenticatedAndActive(permissions.BasePermission):
    """
    Permissions for authenticated users only.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user.is_active:
            raise PermissionDenied("Invalid credentials.")
        return True