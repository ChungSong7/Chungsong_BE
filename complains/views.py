from rest_framework import viewsets, permissions, generics,status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404, UpdateAPIView
from users.models import User
from .models import Complain
from posts.models import Post,Comment
from .serializers import ComplainSerializer

from boards.paginations import CustomCursorPagination
from users.authentications import extract_user_from_jwt

from .permissions import IsOkayComplain
from administrators.permissions import IsAdmin

#GET 신고 리스트 조회 POST 신고 하기
class ComplainView(APIView): 
    permission_classes = [IsOkayComplain]
    
    def get(self, request, *args, **kwargs):
        complains = Complain.objects.all().order_by('-created_at')
        paginator = CustomCursorPagination()
        paginated_queryset = paginator.paginate_queryset(complains, request)
        serializer = ComplainSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)  # 직렬화된 데이터를 Response에 담아 반환

    def post(self, request, *args, **kwargs): #신고대상 id, jwt, category
        user=extract_user_from_jwt(request)
        if user.status=='정지':
            return Response({'message':'정지 기간에는 신고할 수 없습니다.'})
        
        serializer = ComplainSerializer(data=request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "신고가 접수되었습니다."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    


#PATCH 신고 확인! status 변화 API, 
class ComplainCheckView(APIView):
    permission_classes=[IsAdmin]
    def patch(self,request):
        complain=get_object_or_404(Complain,complain_id=request.data['complain_id'])
        complain.status='처리완료'
        complain.save()
        return Response({'message':'신고 처리 완료'},status=status.HTTP_200_OK)