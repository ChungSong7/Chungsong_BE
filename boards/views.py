from rest_framework import  status,generics
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.exceptions import NotFound



from .models import Board
from .serializers import BoardSerializer
from .permissions import IsOkayBlockedPatch

from users.authentications import extract_user_from_jwt

from posts.models import Post
from posts.serializers import PostSerializer

from django.utils import timezone

from .paginations import CustomCursorPagination
from django.db.models import Case, When, Value, IntegerField
#게시판 종류 list 조회
class BoardView(APIView):
    permission_classes=[IsOkayBlockedPatch]
    
    def get(self,request):
        #공동 게시판 9개 list 주기
        queryset = Board.objects.filter(board_id__lte=9)
        serializer=BoardSerializer(queryset,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    '''
    def get(self, request):
        # 1부터 9까지의 board_id를 순서대로 가져옵니다.
        ordered_boards = Board.objects.filter(board_id__lte=9)
        # 한국어인 board_name을 가진 게시판들을 가져와서 board_name을 기준으로 정렬합니다.
        #school_boards = Board.objects.filter(board_id__gt=9).order_by('board_name')
        school_boards = Board.objects.filter(board_id__gte=10, board_name__regex=r'^[가-힣]')

        queryset = (ordered_boards | school_boards).annotate(
            order=Case(
                When(board_id__lte=9, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            )
        ).order_by('order', '-board_id', 'board_name')
        # 위에서 정의한 두 쿼리셋을 하나의 쿼리셋으로 합칩니다.
        #queryset = ordered_boards | school_boards

        # Serializer를 통해 데이터를 직렬화합니다.
        serializer = BoardSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    '''


class BoardPostsView(generics.ListAPIView):
    permission_classes=[IsOkayBlockedPatch]
    serializer_class = PostSerializer
    pagination_class=CustomCursorPagination
    
    #게시판 별 게시글 list 조회
    def get_queryset(self):
        board_id = self.kwargs['board_id']  # URL에서 전달된 board_id를 가져옴
        return Post.objects.filter(board_id=board_id,display=True)
    
class MySchoolBoardView(generics.ListAPIView):
    permission_classes=[IsOkayBlockedPatch]
    serializer_class = PostSerializer
    pagination_class=CustomCursorPagination
    #개인 학교게시판
    def get_queryset(self):
        user=extract_user_from_jwt(self.request)
        try:
            board=Board.objects.get(board_name=user.school)
            return Post.objects.filter(board_id=board.board_id,display=True)
        except Board.DoesNotExist:
            raise NotFound({'message':'등록된 학교의 게시판이 없습니다. 관리자에게 문의해주세요'})

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