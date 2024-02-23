from rest_framework import  status
from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import User,Notice
from users.serializers import UserSerializer
from .permissions import IsAdmin,RequestPermission
from .serializers import RoomRequestSerializer,FrozenHistorySerializer
from .models import RoomRequest,FreezeHistory
from django.shortcuts import get_object_or_404
from users.authentications import extract_user_from_jwt
from posts.models import Post,Comment
from posts.serializers import PostSerializer
from boards.paginations import CustomCursorPagination
from .school_list import SCHOOL_LIST

from datetime import timedelta
from django.utils import timezone

from django.db.models import Q



class NewUserView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    # 가입 신청 list 조회
    def get(self, request):
        paginator = CustomCursorPagination()
        paginated_queryset = paginator.paginate_queryset(self.queryset, request)
        serializer = self.serializer_class(paginated_queryset, many=True)  # 쿼리셋을 직렬화하여 Serializer 객체 생성
        return paginator.get_paginated_response(serializer.data)  # 직렬화된 데이터를 Response에 담아 반환

    #가입 허가 처리
    def patch(self, request):
        new_user_id=request.data['user_id']
        new_user=get_object_or_404(User,user_id=new_user_id)
        new_user.status='사생인증'
        new_user.save()

        serializer = self.serializer_class(new_user)
        return Response(serializer.data)

    #가입 거부 처리
    def delete(self, request, *args, **kwargs):
        new_user_id=request.data['user_id']
        new_user=get_object_or_404(User,user_id=new_user_id)
        new_user.delete()
        
        return Response({'message':f'{new_user.username} 님이 가입 거부 처리되었습니다.'},status=status.HTTP_204_NO_CONTENT)

class RoomRequestView(APIView):
    serializer_class = RoomRequestSerializer
    permission_classes = [RequestPermission]

    #호수변동 신청 create
    def post(self, request):
        user = extract_user_from_jwt(request)
        new_room = request.data.get('new_room')
        data = {
                'user': user.user_id,
                'pre_room': user.room,
                'new_room': new_room,
            }
        serializer = self.serializer_class(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()  # 호수 변동 신청 생성
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #호수변동 신청 list 조회
    def get(self, request):
        queryset=RoomRequest.objects.all()
        paginator = CustomCursorPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer=self.serializer_class(paginated_queryset,many=True)
        return paginator.get_paginated_response(serializer.data)
    
    #호수변동 처리
    def patch(self,request):
        room_request_id=request.data['room_request_id']
        room_request=get_object_or_404(RoomRequest,room_request_id=room_request_id)
        room_request.status=1
        room_request.user.room=room_request.new_room
        room_request.user.save()
        room_request.save()
        return Response({'message':'호실 변동 처리 완료'},status=status.HTTP_204_NO_CONTENT)
    

class FreezeView(APIView):
    permission_classes = [IsAdmin]
    #정지먹이기
    def patch(self,request):
        user_id = request.data.get('user_id')
        freeze_days = request.data.get('freeze_days')
        user=get_object_or_404(User,user_id=user_id)
        if user.status=='사생인증':
            user.suspension_end_date = timezone.now() + timedelta(days=int(freeze_days))
            user.status='정지'
        elif user.status=='정지':
            user.suspension_end_date += timedelta(days=int(freeze_days))
        complained_size=user.complained
        user.complained=0 #피신고수 청산
        user.save()
        # 정지 히스토리 객체 생성
        freeze=FreezeHistory.objects.create(
            user=user,
            complained_size=complained_size,
            end_date=user.suspension_end_date, 
            days=int(freeze_days)
        )
        notice_data = {
            'user': freeze.user,  # 정지 먹은 유저
            'root_id': freeze.freeze_history_id,  # 정지 기록의 고유 ID
            'category': '정지',  # 알림 카테고리
        }
        Notice.objects.create(**notice_data)


        return Response({"message": f"{user.username}님이 {freeze_days}일간 정지되었습니다."}, status=status.HTTP_200_OK)
    
    #정지 이력 조회
    def get(self,request,user_id,*args, **kwargs):
        user_id=self.kwargs['user_id']
        user = get_object_or_404(User, user_id=user_id)
        queryset = FreezeHistory.objects.filter(user=user).order_by('-created_at')
        paginator = CustomCursorPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = FrozenHistorySerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)

class AdminDeleteView(APIView):
    permission_classes=[IsAdmin]
    #게시글 or 댓글 완전삭제
    def delete(self,request):
        post_id = request.data.get('post_id')
        comment_id = request.data.get('comment_id')

        if post_id and not comment_id:
            post=get_object_or_404(Post,post_id=post_id)
            post.delete()
            return Response({'message':'게시글이 완전 삭제되었습니다.'})
        elif not post_id and comment_id:
            comment=get_object_or_404(Comment,comment_id=comment_id)
            #게시글의 댓글 수 재조정
            post=comment.post
            comment.delete()
            print(post.comment_size)
            post.comment_size = Comment.objects.filter(post=post, display=True).count()
            print(post.comment_size)
            post.save()
            return Response({'message':'댓글이 완전 삭제되었습니다.'})
        else:
            return Response({'message':'유효한 post_id 또는 comment_id 를 전달하세요'})
        
    #휴지통 조회(삭제된)
    def get(self,request):
        deleted_comments = Comment.objects.filter(display=False)
        deleted_comment_posts = deleted_comments.values_list('post_id', flat=True).distinct()
        deleted_posts = Post.objects.filter(Q(display=False)|Q(post_id__in=deleted_comment_posts)).order_by('-created_at').distinct()
        
        paginator = CustomCursorPagination()
        paginated_queryset = paginator.paginate_queryset(deleted_posts, request)
        serializer = PostSerializer(paginated_queryset, many=True)

        return paginator.get_paginated_response(serializer.data)
    
class SchoolListView(APIView):
    def get(sefl,request):
        return Response(SCHOOL_LIST)