from rest_framework import permissions
from users.authentications import extract_user_from_jwt

#[인증대기, 사생인증, 관리자, 정지, 학생회]

#GET DELETE 인증대기 빼고 전부  & PATCH 전부
class UserInfoPermit(permissions.BasePermission):
    def has_permission(self, request, view):
        #GET 조회, DELETE 탈퇴 자격
        if request.method in ['GET','DELETE']:
            user=extract_user_from_jwt(request)
            return user.status in ['사생인증','정지','학생회','관리자']
        # 이메일,비번 변경 은 다 가능
        elif request.method=='PATCH':
            return True
        #다른 METHOD는 거부! 
        return False