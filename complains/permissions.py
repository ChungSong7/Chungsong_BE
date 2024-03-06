from rest_framework import permissions
from users.authentications import extract_user_from_jwt

from rest_framework.response import Response
from rest_framework import status

from posts.models import Post,Comment
from django.core.exceptions import ObjectDoesNotExist

#[인증대기, 사생인증, 관리자, 정지, 학생회]

#GET 관리자만. & POST 사생인증, 관리자, (학생회)
class IsOkayComplain(permissions.BasePermission):
    def has_permission(self, request, view):
        user=extract_user_from_jwt(request)
        #GET 관리자만 신고조회
        if request.method == 'GET':
            return user.status == '관리자'
        #POST 작성은 정지 회원 빼고 가능 : 정지 거부 message 응답 주기
        elif request.method=='POST':
            return user.status in ['사생인증','학생회','관리자','정지']
        #다른 HTTO 메서드는 거부! 
        return False 
