from rest_framework import viewsets, permissions, generics,status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework.generics import get_object_or_404, UpdateAPIView
from users.models import User
from .models import Complain
from posts.models import Post,Comment
from .serializers import ComplainSerializer

from administrators.permissions import IsAdmin

'''
def can_complain(request):
    # request.kwargs['user_id'] 얘는 없으면 KeyError 발생
    #게시글 존재 여부
    comp_post_id=
    if request.data['comp_post_id']:
        try:
            post=Post.objects.get(post_id=post_id) #영구삭제는 아닌데,
            if not post.display: #display 가 False일때
                return Response({"error": "이미 삭제된 게시글입니다."}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist: #영구삭제일 때
            return Response({"error": "이미 삭제된 게시글입니다."}, status=status.HTTP_200_OK)
    #댓글 존재 여부
    comment_id=request.parser_context['kwargs'].get('comment_id')
    if comment_id:
        try:
            comment=Comment.objects.get(comment_id=comment_id)
            if not comment.display:
                return Response({"error": "이미 삭제된 댓글입니다."},status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response({"error": "이미 삭제된 댓글입니다."},status=status.HTTP_200_OK)
    #문제 없음
    return None

'''

class TempView(APIView):
    def get(self, request):
        return Response({'message':'hello world!'})

class ComplainView(APIView): #신고 리스트를 조회
    #permission_classes = [IsAdmin]
    #게시글 or 게시물 존재하는지 검사 하세요.
    
    def post(self, request, *args, **kwargs): #신고대상 id, jwt, category

        serializer = ComplainSerializer(data=request.data,context={'request':request})
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"message": "신고가 접수되었습니다."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class FreezeView(APIView): #신고 처리, 
    permission_classes=[IsAdmin]
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

