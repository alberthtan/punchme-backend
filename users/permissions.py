from rest_framework import permissions
from users.models import User

class StaffPermissions(permissions.BasePermission):
    """
    Permissions for staff.
    """
    def has_permission(self, request, view):
        return request.user.is_staff
    
class CustomerPermissions(permissions.BasePermission):
    """
    Permissions for customers only.
    """
    def has_permission(self, request, view):
        return request.user.role == User.Role.CUSTOMER
    
class ManagerPermissions(permissions.BasePermission):
    """
    Permissions for managers only.
    """
    def has_permission(self, request, view):
        return request.user.role == User.Role.MANAGER
    
class IsAuthenticatedAndActive(permissions.BasePermission):
    """
    Permissions for authenticated users only.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_active