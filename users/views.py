from rest_framework.views import APIView
from rest_framework.authentication import get_authorization_header
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializers import UserSerializer,UserUpdateSerializer,UserExistenceCheckSerializer
from .models import User
from .authentications import create_access_token,create_refresh_token,decode_access_token,decode_refresh_token,extract_user_from_jwt
import re
from django.contrib.auth.hashers import make_password,check_password
from django.shortcuts import get_object_or_404

#from django.contrib.auth import logout

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
        
        

#jwt 유저정보 조회,삭제 API
class UserInfoView(APIView):

    #유저정보 조회
    def get(self,request):
        user=extract_user_from_jwt(request)
        serializer=UserSerializer(user)
        return Response(serializer.data)
    
    #유저정보 수정(email, password) !!!반드시 POST UserMatchingView 호출 후에만 호출할 것!!!
    def patch(self, request):
        user_serializer = UserExistenceCheckSerializer(data=request.data)
        update_serializer = UserUpdateSerializer(data=request.data, partial=True)
        
        if user_serializer.is_valid(raise_exception=True):
            user = user_serializer.validated_data
        if update_serializer.is_valid(raise_exception=True):
            response=update_serializer.update(user, update_serializer.validated_data)
        
        return response
    
    #회원탈퇴
    def delete(self,request):
        #너가 누군지 jwt로 찾을게
        user=extract_user_from_jwt(request)
        password = request.data.get('password', None)
        if not password:
            return Response({'error': 'please input password'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password): #비밀번호 올바르게 입력했니?
            raise AuthenticationFailed('!비밀번호가 일치하지 않습니다.')    
        #계정삭제
        user.delete()
        #로그아웃
        response = Response({'message': '회원탈퇴가 성공적으로 처리되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(key='refresh_token')
        return response

    

#access_token 재발급 API
class RefreshJWTTokenView(APIView):
    def post(self, request):
        refresh_token=request.COOKIES.get('refresh_token')
        user_id=decode_refresh_token(refresh_token)
        access_token=create_access_token(user_id)
        return Response({
            'message':'access_token refresh success',
            'access_token':access_token
            })

#로그아웃 API
class LogoutView(APIView):
    def post(self, request):
        response=Response({'message':'logout success'})
        response.delete_cookie(key='refresh_token')
        return response
    
#회원가입 - 별명 중복 검사 API
class NickDupCheckView(APIView):

    def get(self, request):
        nickname=request.GET.get('nickname', None)
        if not nickname:
            return Response({'error': 'please input nickname'}, status=status.HTTP_400_BAD_REQUEST)
        if bool(re.match('^[\uac00-\ud7a3]+$', nickname)):
            try:
                User.objects.get(nickname=nickname) #get이 객체 없으면 얘외 발생 시켜주는 애라서 ㄱㅊ
                return Response({'message':'The nickname is already taken'})
            except User.DoesNotExist:
                return Response({'message':'The nickname is available for use'})
        return Response({"message":"Nickname should be Korean without spaces"})


class UserMatchingView(APIView):
    #로그인 전 email 찾기
    def get(self, request):
        # 이름과 호실을 받아서 이메일 반환
        username = request.query_params.get('username')
        room = request.query_params.get('room')
        user = get_object_or_404(User,username=username, room=room) # 없으면 not fount 메시지 줌
        email=user.email
        #email mask
        email_id, domain = email.split('@')
        masked_email_id = email_id[:4] + '*' * (len(email_id) - 4)
        masked_email = masked_email_id + '@' + domain
        return Response({'message':'조회 성공','masked_email': masked_email})

    def post(self, request):
        serializer = UserExistenceCheckSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data
            print(user)
            return Response({'message': 'User exists', 'username': user.username,'room':user.room,'email':user.email,'school':user.school})
        # 이름, 호실, 이메일을 받아서 유저의 존재 여부 확인
        else:
            return Response({'message': 'User not found'}, status=404)


class ChangeCredentialsView(APIView):

    #authentication_classes = [JWTAuthentication]
    #permission_classes = [IsAuthenticated]  얘네 꼭 필요한 지 잘 모르겠음
    def patch(self, request):    
        serializer = UserExistenceCheckSerializer(data=request.data)
        if serializer.is_valid():
            # 시리얼라이저의 validate 메서드를 통해 유저의 존재 여부 확인
            user = serializer.validated_data
            print(type(user))
            print(user)
            return Response({'message': '유저가 존재합니다.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
        

        new_email = request.data.get('new_email')
        password = request.data.get('password')
        print(password)
        password_confirm = request.data.get('password_confirm')
        print(password_confirm)

        #email 변경 요청 처리
        if new_email:
            print(6)
            if user.email!=new_email:
                print(7)
                old_email=user.email
                user.email = new_email #이메일 변경
                user.save()
                return Response({"message":old_email+" -> "+new_email+"로 이메일 변경 완료"})
            else:
                return Response({"error":"기존 email과 다른 email을 입력해주세요. "})

        # 비밀번호 변경 요청 처리
        elif password and password_confirm:
            #비밀번호 10자리 조건 확인
            if len(password) < 10 or len(password_confirm) < 10:
                return Response({'error':'비밀번호는 10자 이상이어야 합니다.'})
            #비밀번호 요구조건 확인
            if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{10,}$', password):
                return Response({'error':'비밀번호는 영문, 숫자, 특수문자를 각각 한 개 이상 포함하여야 합니다.'})
            #새로운 비밀번호가 일치하는지 확인
            if password != password_confirm:
                return Response({'error': '비밀번호와 비밀번호 확인이 일치하지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            #기존 비밀번호랑 같은지? 
            if make_password(password) == user.password:
                return Response({'error':'기존 비밀번호와 다른 비밀번호를 입력하세요.'})
            else:
                user.set_password(password) #해싱 저장
                user.save()
                return Response({'message':'비밀번호가 변경되었습니다.'})
        return Response({'message':'뭣도 아님'})