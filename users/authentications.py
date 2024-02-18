from my_settings import ACCESS_TOKEN_SECRET_KEY,REFRESH_TOKEN_SECRET_KEY, ALGORITHM
import jwt, datetime
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header
from .models import User
from django.shortcuts import get_object_or_404

#access_token 생성
def create_access_token(user_id):
    payload={
        'user_id':user_id,
        'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=180), #3시간 access 토큰 유지
        'iat':datetime.datetime.utcnow()
    }
    token=jwt.encode(payload,ACCESS_TOKEN_SECRET_KEY,algorithm=ALGORITHM)
    return token

#access_token 디코딩->user_id 리턴
def decode_access_token(token):
    try:
        payload= jwt.decode(token,ACCESS_TOKEN_SECRET_KEY,algorithms=ALGORITHM)
        return payload['user_id']
    except:
        raise exceptions.AuthenticationFailed('access_token unauthenticated')

#refresh_token 생성
def create_refresh_token(user_id):
    payload={
        'user_id':user_id,
        'exp':datetime.datetime.utcnow()+datetime.timedelta(days=90), #3달 refresh 토큰 유지
        'iat':datetime.datetime.utcnow()
    }
    token=jwt.encode(payload,REFRESH_TOKEN_SECRET_KEY,algorithm=ALGORITHM)
    return token

#refresh_token 디코딩 -> user_id 리턴
def decode_refresh_token(token):
    try:
        payload=jwt.decode(token,REFRESH_TOKEN_SECRET_KEY,algorithms=ALGORITHM)
        return payload['user_id']
    except:
        raise exceptions.AuthenticationFailed('refresh token unauthenticated')
    
#request에서 jwt로 유저객체 찾아서 리턴
def extract_user_from_jwt(request):
    auth=get_authorization_header(request).split()
    if auth and len(auth)==2: #auth[0]=='Bearer'
            token=auth[1].decode('utf-8') #토큰 추출
            user_id=decode_access_token(token) #토큰에서 유저 고유번호 추출
            user=get_object_or_404(User,user_id=user_id)
            user.update_status()
            return user
    return exceptions.AuthenticationFailed('access_token unauthenticated')