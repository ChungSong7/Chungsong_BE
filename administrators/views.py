from rest_framework import  status
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import User
from users.serializers import UserSerializer
from .permissions import IsAdmin,RequestPermission
from .serializers import RoomRequestSerializer
from .models import RoomRequest
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

class RoomRequestView(APIView):
    #serializer_class = RoomRequestSerializer
    permission_classes = [RequestPermission]

    #호수변동 신청 create
    def post(self, request):
        user = extract_user_from_jwt(request)
        new_room = request.data.get('new_room')
        data = {
                'user': user.user_id,
                'pre_room': user.room,
                'new_room': new_room,
            }
        serializer = RoomRequestSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()  # 호수 변동 신청 생성
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #호수변동 신청 list 조회
    def get(self, request):
        queryset=RoomRequest.objects.all()
        serializer=RoomRequestSerializer(queryset,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    #호수변동 처리
    def patch(self,request):
        room_request_id=request.data['room_request_id']
        room_request=get_object_or_404(RoomRequest,room_request_id=room_request_id)
        room_request.status=1
        room_request.user.room=room_request.new_room
        room_request.user.save()
        room_request.save()
        return Response({'message':'호실 변동 처리 완료'},status=status.HTTP_204_NO_CONTENT)

class temp(APIView):
    def get(self,request):
        user=extract_user_from_jwt(request)
        print(user.status)
        return Response