from rest_framework.views import APIView
from rest_framework.authentication import get_authorization_header
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializers import UserSerializer
from .models import User
from .authentications import create_access_token,create_refresh_token,decode_access_token,decode_refresh_token

#회원가입 API
class SignupView(APIView):
    def post(self, request):
        serializer=UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) #유효하지 않을 경우 예외 발생
        user= serializer.save()

        #회원가입 & 동시 로그인
        access_token=create_access_token(str(user.user_id)) #얘는 시리얼라이저 데이터로
        refresh_token=create_refresh_token(str(user.user_id)) #얘는 쿠키로!

        response=Response()
        response.set_cookie(key='refresh_token',value=refresh_token,httponly=True)
        response.data={
            'message':'signup & login success',
            'status':user.status,
            'access_token':access_token
        }
        return response

#로그인 API
class LoginView(APIView):
    def post(self,request):
        email=request.data['email']
        password=request.data['password']

        #해당유저가 있나
        user=User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed('User not found')
        #비번은 맞나
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password')
        
        access_token=create_access_token(str(user.user_id)) #얘는 시리얼라이저 데이터로
        refresh_token=create_refresh_token(str(user.user_id)) #얘는 쿠키로!

        response=Response()
        response.set_cookie(key='refresh_token',value=refresh_token,httponly=True)
        response.data={
            'message':'login success',
            'access_token':access_token
        }
        return response
        #serializer=UserSerializer(user)
        #return Response(serializer.data)
        
    
class UserInfoView(APIView):
    def get(self,request):
        auth=get_authorization_header(request).split()
        if auth and len(auth)==2: #auth[0]=='Bearer'
            token=auth[1].decode('utf-8') #토큰 추출
            user_id=decode_access_token(token) #토큰에서 유저 고유번호 추출
            user=User.objects.get(user_id=user_id) #filter().first()랑 같어 어차피
            serializer=UserSerializer(user)
            return Response(serializer.data)
        
        raise AuthenticationFailed('unauthenticated')

class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token=request.COOKIES.get('refresh_token')
        user_id=decode_refresh_token(refresh_token)
        access_token=create_access_token(user_id)
        return Response({
            'message':'access_token refresh success',
            'access_token':access_token
            })

class LogoutView(APIView):
    def post(self, request):
        response=Response()
        response.delete_cookie(key='refresh_token')
        response.data={
            'message':'logout success'
        }
        return response