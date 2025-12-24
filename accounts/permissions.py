from rest_framework.permissions import BasePermission

class IsAdmin:
    def has_permission(self, request, view):
        return hasattr(request.user, 'vai_tro') and request.user.vai_tro == 'Admin'

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.vai_tro == 'Nhân viên'

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.vai_tro == 'Khách hàng'
