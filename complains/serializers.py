from rest_framework import serializers
from .models import Complain
from django.shortcuts import get_object_or_404

from posts.models import Post,Comment
from boards.models import Board

from users.serializers import UserSerializer
from posts.serializers import PostSerializer

from users.authentications import extract_user_from_jwt
#from comment.serializers import CommentSerializer
from django.core.exceptions import ObjectDoesNotExist


class ComplainSerializer(serializers.ModelSerializer):
    board_id=serializers.SerializerMethodField(required=False)

    comp_post_id = serializers.UUIDField(required=False)
    comp_comment_id = serializers.UUIDField(required=False)

    comp_user_id=serializers.UUIDField(required=False)
    comped_user_id=serializers.UUIDField(required=False)

    comped_user_name=serializers.SerializerMethodField(required=False)
    
    tag=serializers.SerializerMethodField(required=False)
    class Meta:
        model=Complain
        fields=['board_id','complain_id','comp_user_id','comped_user_id','comped_user_name','created_at','status',
                'category','comp_post_id','comp_comment_id','tag',]
        
    def get_board_id(self,obj):
        comped_post=Post.objects.get(post_id=obj.comp_post_id)
        board=comped_post.board
        return board.board_id
        
    def get_tag(self,obj):
        if obj.comp_comment_id:
            comment = Comment.objects.get(comment_id=obj.comp_comment_id)
            return f"{comment.post.board.board_name} 댓글"
        elif obj.comp_post_id:
            post = Post.objects.get(post_id=obj.comp_post_id)
            return f"{post.board.board_name} 게시글"
        
    def get_comped_user_name(self,obj):
        if obj.comp_comment_id:
            comment = Comment.objects.get(comment_id=obj.comp_comment_id)
            if comment.writer==None or comment.writer.status=='탈퇴회원':
                return '탈퇴회원'
            return comment.commenter
        elif obj.comp_post_id:
            post = Post.objects.get(post_id=obj.comp_post_id)
            if post.author==None or post.author.status=='탈퇴회원':
                return '탈퇴회원'
            return post.author.nickname if not post.anon_status else "익명"
        


    def validate(self, data):  #게시글, 댓글 중 1 신고 맞지? 확인
        comp_post_id = data.get('comp_post_id')
        comp_comment_id = data.get('comp_comment_id')
        comp_user=extract_user_from_jwt(self.context['request']) #신고자

        if comp_comment_id and not comp_post_id:
            try:
                comped_comment=Comment.objects.get(comment_id=comp_comment_id) #영구삭제는 아닌데,
                if not comped_comment.display: #display 가 False일때
                    raise serializers.ValidationError({'message':'이미 삭제된 댓글입니다.'})
                if comped_comment.writer==comp_user:
                    raise serializers.ValidationError({'message':'자신의 댓글은 신고 할 수 없습니다.'}) # 일어날 일 X
                if Complain.objects.filter(comp_comment=comped_comment,comp_user=comp_user).exists():
                    raise serializers.ValidationError({'message':'이미 신고한 댓글입니다.'})
            except ObjectDoesNotExist: #영구삭제일 때
                raise serializers.ValidationError({'message':'이미 삭제된 댓글입니다.'})
        elif comp_post_id and not comp_comment_id:
            try:
                comped_post=Post.objects.get(post_id=comp_post_id) #영구삭제는 아닌데,
                if not comped_post.display: #display 가 False일때
                    raise serializers.ValidationError({'message':'이미 삭제된 게시글입니다.'})
                if comped_post.author==comp_user:
                    raise serializers.ValidationError({'message':'자신의 게시글은 신고 할 수 없습니다.'}) #일어날 일 X
                if Complain.objects.filter(comp_post=comped_post,comp_user=comp_user).exists():
                    raise serializers.ValidationError({'message':'이미 신고한 게시글입니다.'})
            except ObjectDoesNotExist: #영구삭제일 때
                raise serializers.ValidationError({'message':'이미 삭제된 게시글입니다.'})
        else:
            raise serializers.ValidationError({'message':'게시글과 댓글 중 하나만 신고하세요.'}) # 일어날 일 X
        return data

    def create(self, validated_data):
        comp_post_id = validated_data.get('comp_post_id')
        comp_comment_id = validated_data.get('comp_comment_id')
        category = validated_data.get('category')

        # 게시글과 댓글 ID 중 하나가 있는 경우에만 해당 모델 "인스턴스"를 할당
        if comp_post_id and not comp_comment_id: #게시글 신고일 때

            comp_post = Post.objects.get(post_id=comp_post_id)
            comp_comment=None
            comped_user=comp_post.author

        elif comp_comment_id and not comp_post_id: #댓글 신고일 때
            comp_comment = Comment.objects.get(comment_id=comp_comment_id)
            comp_post=comp_comment.post
            comped_user=comp_comment.writer

        complain = Complain.objects.create(
            comp_post=comp_post,
            comp_comment=comp_comment,
            comp_user=extract_user_from_jwt(self.context['request']), # 현재 신고 요청한 사용자
            comped_user=comped_user,
            category=category,
            status=0  # 대기중
        )
        #(글,댓,유저) 신고수 재조정
        if comp_post_id:
            #게시글 신고 수 조정
            comp_post.warn_size = Complain.objects.filter(comp_post=comp_post).count()
            comp_post.save()
            comped_user.complained=Complain.objects.filter(comped_user=comped_user).count()
            comped_user.save()
        elif comp_comment_id:
            #댓글 신고 수 조정
            comp_comment.warn_size = Complain.objects.filter(comp_comment=comp_comment).count()
            comp_comment.save()
            comped_user.complained=Complain.objects.filter(comped_user=comped_user).count()
            comped_user.save()
        return complain