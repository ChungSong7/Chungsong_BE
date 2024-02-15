from rest_framework import viewsets, permissions, generics,status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404, UpdateAPIView
from users.models import User
from .models import Complain
from .serializers import ComplainSerializer, ComplainCreateSerializer, ComplainStatusSerializer

class IsAdminUserOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.status == '관리자'

class ComplainListAPI(APIView): #신고 리스트를 조회
    permission_classes = [IsAdminUserOnly]

    def get(self,request):
        complains = Complain.objects.all()
        serializer = ComplainSerializer(complains, many= True)
        return Response(serializer.data, status = status.HTTP_200_OK)
    
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
       

        
    

