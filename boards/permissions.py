from rest_framework import permissions
from users.authentications import extract_user_from_jwt

from rest_framework.response import Response
from rest_framework import status

from posts.models import Post,Comment
from django.core.exceptions import ObjectDoesNotExist

#[인증대기, 사생인증, 관리자, 정지, 학생회]

#GET 인증대기 빼고 전부 (조회) & POST 사생인증, 관리자, (학생회)
class IsOkayBlockedPatch(permissions.BasePermission):
    def has_permission(self, request, view):
        user=extract_user_from_jwt(request)
        #GET 조회는 인증대기 빼고 전부 가능
        if request.method==('GET'or'PATCH'):
            print(1)
            return user.status in ['사생인증','정지','학생회','관리자']
        #POST 작성은 정지 회원 빼고 가능
        elif request.method=='POST':
            print(3)
            return user.status in ['사생인증','학생회','관리자']
        #다른 HTTO 메서드는 거부! 
        return False 

#PATCH 좋아요 막으려고.
class IsOkayLike(permissions.BasePermission):
    def has_permission(self, request, view):
        user=extract_user_from_jwt(request)
        #GET 조회는 인증대기 빼고 전부 가능
        if request.method=='PATCH':
            return user.status in ['사생인증','학생회','관리자']
        #다른 HTTO 메서드는 거부! 
        return False 
'''

'''


