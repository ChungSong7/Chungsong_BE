from rest_framework import  status
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import User
from users.serializers import UserSerializer
from .permissions import IsAdmin
from django.shortcuts import get_object_or_404
from users.authentications import extract_user_from_jwt



class NewUserView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    #가입 신청 list 조회
    def get(self, request):
        queryset = User.objects.filter(status='인증대기')  # 필터링된 쿼리셋 가져오기
        serializer = UserSerializer(queryset, many=True)  # 쿼리셋을 직렬화하여 Serializer 객체 생성
        return Response(serializer.data, status=status.HTTP_200_OK)  # 직렬화된 데이터를 Response에 담아 반환

    #가입 허가 처리
    def patch(self, request):
        new_user_id=request.data['user_id']
        new_user=get_object_or_404(User,user_id=new_user_id)
        new_user.status='사생인증'
        new_user.save()

        serializer = UserSerializer(new_user)
        return Response(serializer.data)

    #가입 거부 처리
    def delete(self, request, *args, **kwargs):
        new_user_id=request.data['user_id']
        new_user=get_object_or_404(User,user_id=new_user_id)
        new_user.delete()
        
        return Response({'message':f'{new_user.username} 님이 가입 거부 처리되었습니다.'},status=status.HTTP_204_NO_CONTENT)



class temp(APIView):
    def get(self,request):
        user=extract_user_from_jwt(request)
        print(user.status)
        return Response