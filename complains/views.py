from rest_framework import viewsets, permissions, generics,status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404, UpdateAPIView
from users.models import User
from .models import Complain
from posts.models import Post,Comment
from .serializers import ComplainSerializer

from .permissions import IsOkayComplain

class TempView(APIView):
    def get(self, request):
        return Response({'message':'hello world!'})

class ComplainView(APIView): #신고 리스트 조회, 신고 하기
    permission_classes = [IsOkayComplain]
    
    def post(self, request, *args, **kwargs): #신고대상 id, jwt, category
        serializer = ComplainSerializer(data=request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "신고가 접수되었습니다."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, reqiuest, *args, **kwargs):
        complains = Complain.objects.all()
        serializer = ComplainSerializer(complains, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class FreezeView(APIView): #정지 처리, 
    permission_classes=[IsOkayComplain]
    pass

'''
class ComplainCreateAPI(APIView): #신고 작성
    def post(self,request):
        serializer = ComplainCreateSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

class ComplainAPI(APIView): #신고 개별 조회
    permission_classes = [IsAdminUserOnly]

    def get(self,request, complain_id):
        complain = get_object_or_404(Complain,complain_id=complain_id)
        serializer = ComplainSerializer(complain)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ComplainStatusAPI(UpdateAPIView): #신고 상태
    permission_classes = [IsAdminUserOnly]

    def update(self,request, *args, **kwargs):
        complain = self.get_object()
        serializer = ComplainStatusSerializer(complain, data = request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        
    '''

