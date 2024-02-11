from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import ComplainSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Complain

#[POST] 신고하기
class CreateComplainView(APIView):

    #permission 로직 추가 필요
    #모든 사용자가 신고 가능하도록

    def post(self, request):
        serializer = ComplainSerializer(data=request.data)

        serializer.is_valid(raise_exception=True) #유효성 검사 실패
        serializer.save(comp_user=request.user)
        
        return Response({
            'message': '신고가 성공적으로 등록되었습니다.',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)


#[GET] 신고리스트 조회하기
class ComplainListView(APIView):

    #permission 로직 추가
    #관리자만 신고 목록 조회할 수 있도록
    #권한관련 오류 잡는것도 밑에 추가 (try-catch로)

    
    def get(self):
        try:
            complains = Complain.objects.all()
            if not complains:
                return Response({
                    'message': '조회된 신고가 없습니다.',
                    'data': []
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = ComplainSerializer(complains, many=True)
            return Response({
                'message': '신고 목록 조회에 성공했습니다.',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'message': '신고 목록 조회 중 오류 발생'+str(e),
                'data': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
