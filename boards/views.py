from rest_framework import  status,generics
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.exceptions import NotFound

from django.http import JsonResponse

from .models import Board
from .serializers import BoardSerializer
from .permissions import IsUser

from users.authentications import extract_user_from_jwt

from posts.models import Post
from posts.serializers import PostSerializer

from django.utils import timezone

from .paginations import CustomCursorPagination
from django.db.models import Case, When, Value, IntegerField

#게시판 종류 list 조회
class BoardView(APIView):
    permission_classes=[IsUser]
    
    def get(self,request):
        #공동 게시판 9개 list 주기
        queryset = Board.objects.filter(board_id__lte=9)
        serializer=BoardSerializer(queryset,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)


class BoardPostsView(generics.ListAPIView):
    permission_classes=[IsUser]
    serializer_class = PostSerializer
    pagination_class=CustomCursorPagination
    
    #게시판 별 게시글 list 조회
    def get_queryset(self):
        board_id = self.kwargs['board_id']  # URL에서 전달된 board_id를 가져옴
        return Post.objects.filter(board_id=board_id,display=True).order_by('-created_at')

class MySchoolBoardView(generics.ListAPIView):
    permission_classes=[IsUser]
    serializer_class = PostSerializer
    pagination_class=CustomCursorPagination
    #개인 학교게시판
    def get_queryset(self):
        user=extract_user_from_jwt(self.request)
        try:
            board=Board.objects.get(board_name=user.school)
            return Post.objects.filter(board_id=board.board_id,display=True).order_by('-created_at')
        except Board.DoesNotExist:
            raise NotFound({'message':'등록된 학교의 게시판이 없습니다. 관리자에게 문의해주세요'})

class HotPostView(generics.ListAPIView):
    permission_classes=[IsUser]
    serializer_class = PostSerializer
    pagination_class = CustomCursorPagination

    def get_queryset(self):
        # 현재 시간 기준으로 이전 시간을 계산 (예: 7일 전)
        previous_date = timezone.now() - timezone.timedelta(days=7)

        # 좋아요 수가 10개 이상이고, 작성일자가 previous_date 이후인 게시글 필터링
        queryset = Post.objects.filter(like_size__gte=10, created_at__gte=previous_date, board__board_id__range=(1, 9))

        # 시간순으로 정렬
        queryset = queryset.order_by('-created_at')

        return queryset
    
def health_check(request):
    return JsonResponse({'status': 'ok'})