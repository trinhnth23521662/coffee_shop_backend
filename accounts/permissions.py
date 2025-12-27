from rest_framework.permissions import BasePermission

class IsLoggedIn(BasePermission):
    def has_permission(self, request, view):
        return bool(request.session.get('user_id'))

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.session.get('role') == 'Admin'

class IsStaff(BasePermission):
    def has_permission(self, request, view):
        return request.session.get('role') == 'Nhân viên'

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.session.get('role') == 'Khách hàng'
