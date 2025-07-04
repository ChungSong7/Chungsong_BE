from rest_framework.views import APIView
from rest_framework.authentication import get_authorization_header,TokenAuthentication
from rest_framework.response import Response
from rest_framework import status,generics
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer,NoticeSerializer,UserUpdateSerializer
from .models import User,DeletedUser,EmailVarify,Notice
from .authentications import create_access_token,create_refresh_token,decode_access_token,decode_refresh_token,extract_user_from_jwt
import re
from django.contrib.auth.hashers import make_password,check_password
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.utils import timezone
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

from config import settings

from posts.models import Post,Comment
from posts.serializers import PostSerializer

from boards.permissions import IsOkayBlockedPatch
from boards.paginations import CustomCursorPagination

from .permissions import UserInfoPermit
import random


#회원가입 API
class SignupView(APIView):
    def post(self, request):
        serializer=UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) #유효하지 않을 경우 예외 발생
        user= serializer.save()
        #회원가입
        return Response({'message':'회원등록 완료','status':user.status})

#로그인 API
class LoginView(APIView):
    def post(self,request):
        email=request.data['email']
        password=request.data['password']

        #해당유저가 있나
        user=User.objects.filter(email=email).first()
        if user is None:
            raise AuthenticationFailed({'message':'해당 사용자를 찾을 수 없습니다.'})
        #비번은 맞나
        if not user.check_password(password):
            raise AuthenticationFailed({'message':'비밀번호가 틀립니다.'})
        
        if user.status=='인증대기':
            return Response({'message':'회원님은 현재 인증대기 상태입니다.'})
        
        access_token=create_access_token(str(user.user_id)) #얘는 시리얼라이저 데이터로
        refresh_token=create_refresh_token(str(user.user_id)) #얘는 쿠키로!

        response=Response()
        response.set_cookie(key='refresh_token',value=refresh_token,httponly=True)
        response.data={
            'message':'login success',
            'access_token':access_token
        }
        return response      

#jwt 유저정보 조회,삭제/ 변경 API
class UserInfoView(APIView):
    permission_classes=[UserInfoPermit]
    #유저정보 조회
    def get(self,request):
        user=extract_user_from_jwt(request)
        serializer=UserSerializer(user)
        return Response(serializer.data)
        
    #회원탈퇴
    def delete(self,request):
        #너가 누군지 jwt로 찾을게
        user=extract_user_from_jwt(request)
            
        password = request.data.get('password', None)
        if not password:
            return Response({'error': 'please input password'}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password): #비밀번호 올바르게 입력했니?
            raise AuthenticationFailed('Incorrect password')
        
        DeletedUser.objects.create(
            name = user.username,
            email = user.email,
            room = user.room + 10000,
            school = user.school
        )
        #계정 별명, 이메일, 호실 필드 비우기, 권한 바꾸기,
        del_num=DeletedUser.objects.count()
        user.nickname = f'delete{del_num}'
        user.email = f'delete{del_num}@deleted.com'
        user.room = user.room
        user.status = '탈퇴회원'
        user.save()

        #로그아웃
        response = Response({'message': '회원탈퇴가 성공적으로 처리되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie('refresh_token')
        return response
    
    #이메일 또는 비번 변경
    def patch(self,request):
        serializer = UserUpdateSerializer(data=request.data)
        if serializer.is_valid():
            # 현재 요청을 보낸 사용자
            validated_data = serializer.validated_data
            username = validated_data.get('username')
            room = validated_data.get('room')
            email = validated_data.get('email')
            user = get_object_or_404(User, username=username, room=room, email=email)
            try:
                # 유저 정보 업데이트
                response= serializer.update(user, validated_data)
                return response
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

#로그아웃 API : 프론트에서 반드시 access_token 파기해야함
class LogoutView(APIView):
    def post(self, request):
        response=Response({'message':'logout success'})
        response.delete_cookie(key='refresh_token')
        return response
    
#회원가입 - 별명 중복 검사
class NickDupCheckView(APIView):

    def is_korean_only(self, text):
        return bool(re.match('^[\uac00-\ud7a3]+$', text))
    
    def get(self, request):
        nickname=request.GET.get('nickname', None)
        print(nickname)
        if not nickname:
            return Response({'message': '별명을 입력해주세요'}, status=status.HTTP_400_BAD_REQUEST)
        if self.is_korean_only(nickname):
            try:
                User.objects.get(nickname=nickname) #get이 객체 없으면 얘외 발생 시켜주는 애라서 ㄱㅊ
                return Response({'message':f'{nickname} 은(는) 이미 사용중인 닉네임입니다.'})
            except User.DoesNotExist:
                return Response({'message':f'{nickname} 별명 사용 가능'})
        return Response({"message":"별명은 공백이 없는 한글로만 입력해주세요."})
    
#이메일 중복검사
class EmailDupCheckView(APIView): #이메일 바꾸기 전,회원가입 시 이메일 인증 전 호출
    def get(self, request):
        email=request.GET.get('email', None)
        if not email:
            return Response({'message':'이메일을 입력해주세요'})
        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            return Response({'message':'이메일 형식이 맞지 않습니다.'})
        try:
            User.objects.get(email=email) #get이 객체 없으면 얘외 발생 시켜주는 애라서 ㄱㅊ
            return Response({'message':'이미 사용 중인 이메일입니다.'})
        except User.DoesNotExist:
            return Response({'message':'사용 가능한 이메일입니다.'})

#이메일 찾기(조회)
class UserMatchingView(APIView):
    def get(self, request):
        # 이름과 호실을 받아서 이메일 반환
        username = request.query_params.get('username')
        room = request.query_params.get('room')
        try:
            user = User.objects.get(username=username, room=room)
            email=user.email

            #email mask
            email_id, domain = email.split('@')
            #masked_email_id = email_id[:4] + '*' * (len(email_id) - 4)
            #masked_email = masked_email_id + '@' + domain
            masked_email='______' + '@' + domain
            return Response({'message':'조회 성공','masked_email': masked_email})
        except User.DoesNotExist:
            return Response({'message': '입력하신 정보와 일치하는 사용자가 없습니다.'}, status=404)
    
    def post(self, request):
        # 이름, 호실, 이메일을 받아서 유저의 존재 여부 확인
        username = request.data.get('username')
        room = request.data.get('room')
        email = request.data.get('email')
        try:
            user = User.objects.get(username=username, room=room, email=email)
            return Response({'message': '사용자 정보 확인'})
        except User.DoesNotExist:
            return Response({'message': '입력하신 정보와 일치하는 사용자가 없습니다.'}, status=404)

#내가 쓴 글
class MyPostView(generics.ListAPIView):
    permission_classes=[IsOkayBlockedPatch]
    serializer_class = PostSerializer
    pagination_class = CustomCursorPagination

    def get_queryset(self):
        user=extract_user_from_jwt(self.request)
        my_posts=Post.objects.filter(author=user, display=True)
        # 현재 요청한 사용자의 게시글 중 display 속성이 True인 것들만 필터링
        return my_posts.order_by('-created_at')

#내가 댓글 단 글
class MyCommentView(generics.ListAPIView):
    permission_classes=[IsOkayBlockedPatch]
    serializer_class = PostSerializer
    pagination_class = CustomCursorPagination
    def get_queryset(self):
        user= extract_user_from_jwt(self.request)

        my_comments = Comment.objects.filter(writer=user, display=True)
        commented_posts = my_comments.values_list('post_id', flat=True).distinct()

        return Post.objects.filter(post_id__in=commented_posts).order_by('-created_at')

#나의 알림
class MyNoticeView(generics.ListAPIView):
    permission_classes=[IsOkayBlockedPatch]
    serializer_class = NoticeSerializer
    pagination_class=CustomCursorPagination

    def get_queryset(self):
        user = extract_user_from_jwt(self.request)
        return Notice.objects.filter(user=user).order_by('-created_at')
    
#이메일 전송
class SendEmailCodeView(APIView):
    def post(self,request):
        # 요청에서 이메일 주소 받기
        email = request.data.get('email') 
        try:#email 형식만 맞는지 한번 체크해줘!
            email_validator = EmailValidator()
            email_validator(email) 
        except ValidationError:
            return Response({'message':'이메일 형식이 맞지 않습니다.'})
        
        #6자리 랜덤 코드 생성
        code = ''.join(random.choices('0123456789', k=6))

        #EmailVarify 객체 생성 or 업데이트
        try:
            email_varify_obj = EmailVarify.objects.get(email=email)
            email_varify_obj.code = code
            email_varify_obj.created_at= timezone.now()
            email_varify_obj.save()
        except EmailVarify.DoesNotExist:
            EmailVarify.objects.create(email=email, code=code)
        
        # 이메일로 코드 전송
        send_mail(
            '<청송> 이메일 인증 코드',#제목
            f'회원님의 이메일 인증 코드는 {code} 입니다.',#본문
            settings.EMAIL_HOST_USER,#발신 이메일 주소
            [email],#수신 이메일 주소
            fail_silently=False, 
        )
        return Response({"message": "인증 번호 전송"}, status=status.HTTP_200_OK)

#이메일 인증
class CheckEmailCodeView(APIView):
    def delete(self,request):
        # 사용자가 전달한 email과 code 가져오기
        email = request.data.get('email')
        code = request.data.get('code')
        try:
            # email에 해당하는 EmailVarify 객체 찾기
            email_varify_obj = EmailVarify.objects.get(email=email)
            # 현재 시간과 객체의 생성 시간의 차이 계산 (분 단위로 변환)
            time_difference_minutes = (timezone.now() - email_varify_obj.created_at).total_seconds() / 60
            # 시간 차이가 3분 미만이면 코드 비교
            if time_difference_minutes < 3:
                if email_varify_obj.code == code: #인증코드 일치
                    email_varify_obj.delete()
                    return Response({'message': '이메일 인증이 완료되었습니다.'}, status=status.HTTP_200_OK)
                else: #인증코드 불일치
                    return Response({'message': '인증코드가 올바르지 않습니다.'}, status=status.HTTP_400_BAD_REQUEST)
            else: # 시간 초과 응답
                return Response({'message': '인증 시간이 초과되었습니다. 다시 인증해주세요.'}, status=status.HTTP_400_BAD_REQUEST)
        except EmailVarify.DoesNotExist: # 애초에 그런 email 인증 code 발행한 적 없는데?
            return Response({'message': '해당 이메일에 대한 인증 정보가 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)