from rest_framework import permissions
from users.authentications import extract_user_from_jwt
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request,view):
        user=extract_user_from_jwt(request)
        return user.status == '관리자'
    

class RequestPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user=extract_user_from_jwt(request)
        # POST 신청 '사생인증','정지'만 가능
        if request.method == 'POST':
            return user.status in ['사생인증','정지']
        # GET, PATCH ,DELETE 요청 '관리자'만 접근 허용
        elif request.method in ['GET', 'PATCH','DELETE']:
            return user.status == '관리자'
        return False  # 다른 HTTP 메서드는 거부