from my_settings import ACCESS_TOKEN_SECRET_KEY,REFRESH_TOKEN_SECRET_KEY, ALGORITHM
import jwt, datetime
from rest_framework import exceptions


def create_access_token(user_id):
    payload={
        'user_id':user_id,
        'exp':datetime.datetime.utcnow()+datetime.timedelta(minutes=30), #초
        'iat':datetime.datetime.utcnow()
    }
    token=jwt.encode(payload,ACCESS_TOKEN_SECRET_KEY,algorithm=ALGORITHM)
    return token

def decode_access_token(token):
    try:
        payload= jwt.decode(token,ACCESS_TOKEN_SECRET_KEY,algorithms=ALGORITHM)
        return payload['user_id']
    except:
        raise exceptions.AuthenticationFailed('unauthenticated')

def create_refresh_token(user_id):
    payload={
        'user_id':user_id,
        'exp':datetime.datetime.utcnow()+datetime.timedelta(days=7), #일주일 토큰 유지
        'iat':datetime.datetime.utcnow()
    }
    token=jwt.encode(payload,REFRESH_TOKEN_SECRET_KEY,algorithm=ALGORITHM)
    return token

def decode_refresh_token(token):
    try:
        payload=jwt.decode(token,REFRESH_TOKEN_SECRET_KEY,algorithms=ALGORITHM)
        return payload['user_id']
    except:
        raise exceptions.AuthenticationFailed('unauthenticated')