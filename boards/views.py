from rest_framework import  status,generics
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Board
from .serializers import BoardSerializer
from .permissions import IsOkayBlockedPatch

from posts.models import Post
from posts.serializers import PostSerializer

from django.utils import timezone

from .paginations import CustomCursorPagination

#게시판 종류 list 조회
class BoardView(APIView):
    def get(self,request):
        queryset=Board.objects.all()
        serializer=BoardSerializer(queryset,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    



class BoardPostsView(generics.ListAPIView):
    permission_classes=[IsOkayBlockedPatch]
    serializer_class = PostSerializer
    pagination_class=CustomCursorPagination
    
    #게시판 별 게시글 list 조회
    def get_queryset(self):
        board_id = self.kwargs['board_id']  # URL에서 전달된 board_id를 가져옴
        return Post.objects.filter(board_id=board_id,display=True)
    
class HotPostView(generics.ListAPIView):
    permission_classes=[IsOkayBlockedPatch]
    serializer_class = PostSerializer
    pagination_class = CustomCursorPagination

    def get_queryset(self):
        # 현재 시간 기준으로 이전 시간을 계산 (예: 7일 전)
        previous_date = timezone.now() - timezone.timedelta(days=7)

        # 좋아요 수가 10개 이상이고, 작성일자가 previous_date 이후인 게시글 필터링
        queryset = Post.objects.filter(like_size__gte=3, created_at__gte=previous_date)

        # 시간순으로 정렬
        queryset = queryset.order_by('-created_at')

        return queryset