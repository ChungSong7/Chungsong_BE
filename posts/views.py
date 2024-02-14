from rest_framework.generics import CreateAPIView,RetrieveUpdateDestroyAPIView,UpdateAPIView
from rest_framework import status
#from rest_framework.permissions import IsAuthenticated
from .serializers import PostSerializer
from users.authentications import extract_user_from_jwt
from django.shortcuts import get_object_or_404
from .models import Post,PostLiker,Comment
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from boards.permissions import IsOkayBlockedPatch,IsOkayLike

# post display 삭제 검사 함수
def is_exist(request):
    # request.kwargs['user_id'] 얘는 없으면 KeyError 발생
    #게시글 존재 여부
    post_id = request.parser_context['kwargs'].get('post_id') #얘는 없으면 None
    if post_id:
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

#POST 게시글 작성
class PostCreateView(CreateAPIView):
    permission_classes = [IsOkayBlockedPatch]
    serializer_class = PostSerializer
    def post(self, request, board_id, *args, **kwargs):
        # 게시판 객체 가져오기
        # 시리얼라이저에 context 전달
        serializer = self.get_serializer(data=request.data, context={'board_id': board_id, 'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#GET 게시글 단일 조회 // PATCH 게시글 삭제 //DELETE 휴지통삭제 (ㄴㄴ)
class PostView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsOkayBlockedPatch]
    serializer_class = PostSerializer
    
    lookup_url_kwarg = 'post_id' #url에서
    lookup_field = 'post_id' #model에서

    def get_queryset(self):
        board_id = self.kwargs['board_id']
        return Post.objects.filter(board_id=board_id, display=True)

    #게시글 단일 조회
    def get(self, request, post_id, *args, **kwargs):
        reponse=is_exist(request)
        if reponse:
            return reponse
        post = get_object_or_404(Post, post_id=post_id)
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #게시글 삭제(display 속성만 False로 변경)=(관리자 휴지통으로 이동)
    def patch(self,request,board_id,post_id):
        reponse=is_exist(request)
        if reponse:
            return reponse
        post = get_object_or_404(Post,post_id=post_id)
        user=extract_user_from_jwt(request)
        #본인이거나 관리자면 삭제 ㅇㅋ
        if post.author == user or user.status=='관리자':
            post.display = False  # display 필드를 False로 변경
            post.save()
            return Response({"message":"게시글이 삭제되었습니다."},status=status.HTTP_200_OK)
        else:
            return Response({"message":"게시글 본인이 아닌데 삭제 어떻게 접근하셨니?"},status=status.HTTP_200_OK)

#PATCH 게시글 좋아요
class PostLikeView(UpdateAPIView):
    permission_classes=[IsOkayLike]
    serializer_class=PostSerializer

    lookup_url_kwarg = 'post_id' #url에서
    lookup_field = 'post_id' #model에서

    def patch(self,request,post_id, *args, **kwargs):
        reponse=is_exist(request)
        if reponse:
            return reponse
        
        post=get_object_or_404(Post,post_id=post_id)
        user=extract_user_from_jwt(request)
        
        if post.author == user:
            return Response({'message':'자신의 글은 좋아할 수 없습니다.'},status=status.HTTP_200_OK)
        try:
            post.likers.get(user=user)
            return Response({'message':'이미 좋아요를 누른 글입니다.'})
        except ObjectDoesNotExist:
            #좋아하는 사람 목록에 추가
            PostLiker.objects.create(post=post,user=user)
            #게시글 좋아요 수 조정
            post.like_size=post.likers.count()
            post.save()
            return Response({'message':'게시글을 좋아했습니다.'})
