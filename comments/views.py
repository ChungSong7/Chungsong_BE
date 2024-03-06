from rest_framework.generics import CreateAPIView,RetrieveUpdateDestroyAPIView,UpdateAPIView,ListAPIView
from rest_framework import status
from rest_framework.views import APIView
#from rest_framework.permissions import IsAuthenticated
from .serializers import CommentSerializer
from users.authentications import extract_user_from_jwt
from django.shortcuts import get_object_or_404
from posts.models import Post,Commenter,Comment,CommentLiker
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from posts.views import is_exist
from boards.permissions import IsUser
from boards.paginations import CustomCursorPagination

#GET 댓글list 조회  // POST 댓글쓰기
class CommentView(ListAPIView,CreateAPIView):

    permission_classes=[IsUser]
    serializer_class = CommentSerializer
    pagination_class = CustomCursorPagination
    
    #GET 게시글 별 댓글list 조회
    def get(self, request, post_id, *args, **kwargs):
        response = is_exist(request)
        if response:
            return response  # 오류 응답이 반환되었을 때 바로 반환
        # 나머지 로직
        queryset = Comment.objects.filter(post_id=post_id).order_by('-created_at')
        paginator = CustomCursorPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


    #POST 댓글 작성
    def post(self, request, post_id, *args, **kwargs):
        response = is_exist(request)
        if response:
            return response
        
        user=extract_user_from_jwt(request)
        if user.status=='정지':
            return Response({'message':'정지 기간에는 댓글을 작성할 수 없습니다.'})
        context={'post_id': post_id,
                'up_comment_id':request.data.get('up_comment_id'),
                'request':request} #serializer에 넘겨줄 dic


        post=get_object_or_404(Post,post_id=post_id)
        anon_status=request.data.get('anon_status')

        #기작성자인지 확인 함수(user, anon_status로)
        def is_commented(post, user, anon_status): 
            try:
                if anon_status:  # 익명 기작성자?
                    commenter=post.commenters.get(user=user, anon_num__gt=0)
                else:  # 별명 기작성자?
                    commenter=post.commenters.get(user=user, anon_num=0)
                return commenter   # commenter를 찾았을 때
            except ObjectDoesNotExist:
                return False  # commenter를 찾지 못했을 때

        #시리얼라이저에 넘겨줄 commenter, commenter_profile 결정 로직
        if user==post.author:
            context['commenter']='글쓴이'
            context['commenter_profile']=post.author_profile
        else:
            commenter=is_commented(post, user, anon_status)
            if commenter: #기작성자
                if anon_status: #익명 기 작성자
                    context['commenter']='익명'+str(commenter.anon_num)
                else: #별명 기작성자
                    context['commenter']=user.nickname
                context['commenter_profile']=commenter.anon_num
            else : #첫 댓 작성자
                if anon_status: #익명으로 첫댓
                    anon_num=post.commenters.filter(anon_num__gt=0).count()+1
                    context['commenter']='익명'+str(anon_num)
                    context['commenter_profile']=anon_num
                    Commenter.objects.create(post=post,user=user,anon_num=anon_num)
                else:#별명으로 첫댓
                    context['commenter']=user.nickname 
                    context['commenter_profile']=user.profile_image
                    Commenter.objects.create(post=post,user=user,anon_num=0)
        
        #댓글 생성 with serializer
        serializer = self.get_serializer(data=request.data, context=context) #post_id, commenter, commenter_profile 넘겨줌
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#PATCH 댓글 삭제 // DELETE 휴지통삭제(ㄴㄴ)
class CommentDetailView(RetrieveUpdateDestroyAPIView):

    permission_class = [IsUser]
    serializer_class = CommentSerializer
    
    lookup_url_kwarg = 'comment_id'
    lookup_field = 'comment_id'
    
    def get_queryset(self):
        post_id = self.kwargs['post_id']
        return Comment.objects.filter(post_id=post_id, display=True)

    #PATCH 댓글삭제
    def patch(self, request, board_id, post_id, comment_id):
        response = is_exist(request)
        if response:
            return response
        comment = get_object_or_404(Comment, comment_id=comment_id)
        user=extract_user_from_jwt(request)
        if comment.writer == user or user.status=='관리자':
            comment.display = False  # display 필드를 False로 변경
            comment.save()
        else:
            return Response({'message':'너 본인 아닌데 어케 접근했냐?'})
        #게시글 댓글 수 조정
        post=get_object_or_404(Post,post_id=post_id)
        post.comment_size = Comment.objects.filter(post=post, display=True).count()
        post.save()
        return Response({"message":"댓글이 삭제되었습니다."},status=status.HTTP_200_OK)

#PATCH 댓글 좋아요
class CommentLikeView(UpdateAPIView):
    permission_classes=[IsUser]
    serializer_class=CommentSerializer

    lookup_url_kwarg = 'comment_id' #url에서
    lookup_field = 'comment_id' #model에서

    def patch(self,request,comment_id,*args, **kwargs):
        response = is_exist(request)
        if response:
            return response
        user=extract_user_from_jwt(request)
        if user.status =='정지':
            return Response({'message':'정지 기간에는 댓글을 좋아할 수 없습니다.'})

        comment=get_object_or_404(Comment,comment_id=comment_id)

        if comment.writer == user:
            return Response({'message':'자신의 댓글은 좋아할 수 없습니다.'},status=status.HTTP_200_OK)
        try:
            comment.likers.get(user=user)
            return Response({'message':'이미 좋아요를 누른 댓글입니다.'})
        except ObjectDoesNotExist:
            #좋아하는 사람 목록에 추가
            CommentLiker.objects.create(comment=comment,user=user)
            #댓글 좋아요 수 조정
            comment.like_size=comment.likers.count()
            comment.save()
            return Response({'message':'댓글을 좋아했습니다.'})

