from rest_framework import  status,generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Board
from .serializers import BoardSerializer

from posts.models import Post
from posts.serializers import PostDetailSerializer


#게시판 종류 list 조회
class BoardView(APIView):
    def get(self,request):
        queryset=Board.objects.all()
        serializer=BoardSerializer(queryset,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class BoardPostsView(generics.ListAPIView):
    serializer_class = PostDetailSerializer
    #게시판 별 게시글 list 조회
    def get_queryset(self):
        board_id = self.kwargs['board_id']  # URL에서 전달된 board_id를 가져옴
        return Post.objects.filter(board_id=board_id)