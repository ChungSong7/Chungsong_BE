from rest_framework import permissions
from users.authentications import extract_user_from_jwt
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user=extract_user_from_jwt(request)
        print(user.status)
        print('rr')
        return user.status == '관리자'