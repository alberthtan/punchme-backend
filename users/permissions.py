from rest_framework import permissions

class StaffPermissions(permissions.BasePermission):
    """
    Permissions for staff.
    """
    def has_permission(self, request, view):
        return request.user.is_staff