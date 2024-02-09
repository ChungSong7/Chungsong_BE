from rest_framework.generics import CreateAPIView,RetrieveUpdateAPIView
from rest_framework import status
#from rest_framework.permissions import IsAuthenticated
from .serializers import PostSerializer
from users.authentications import extract_user_from_jwt
from django.shortcuts import get_object_or_404
from .models import Post
from rest_framework.response import Response

class PostCreateView(CreateAPIView):
    #permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    def post(self, request, board_id, *args, **kwargs):
        # 게시판 객체 가져오기
        # 시리얼라이저에 context 전달
        serializer = self.get_serializer(data=request.data, context={'board_id': board_id, 'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class PostDetailView(RetrieveUpdateAPIView):
    #permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer

    lookup_url_kwarg = 'post_id'
    lookup_field = 'post_id'

    def get_queryset(self):
        board_id = self.kwargs['board_id']
        return Post.objects.filter(board_id=board_id, display=True)

    #게시글 단일 조회
    def get(self, request, board_id, post_id):
        post = get_object_or_404(Post, post_id=post_id, board_id=board_id)
        if post.display==False:
            return Response({"message":"이미 삭제된 게시글입니다."},status=status.HTTP_200_OK)
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #게시글 삭제(display 속성만 False로 변경)=(관리자 휴지통으로 이동)
    def patch(self,request,board_id,post_id):
        post = get_object_or_404(Post, post_id=post_id, board_id=board_id)
        if post.display==False:
            return Response({"message":"이미 삭제된 게시글입니다."},status=status.HTTP_200_OK)
        post.display = True  # display 필드를 False로 변경
        post.save()

        return Response({"message":"게시글이 삭제되었습니다."},status=status.HTTP_200_OK)
