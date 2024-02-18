from rest_framework import serializers
from .models import Complain
from django.shortcuts import get_object_or_404

from posts.models import Post,Comment

from users.serializers import UserSerializer
from posts.serializers import PostSerializer

from users.authentications import extract_user_from_jwt
#from comment.serializers import CommentSerializer
from django.core.exceptions import ObjectDoesNotExist


class ComplainSerializer(serializers.ModelSerializer):
    comp_post_id = serializers.UUIDField(required=False)
    comp_comment_id = serializers.UUIDField(required=False)
    
    comp_user_id=serializers.UUIDField(required=False)
    comped_user_id=serializers.UUIDField(required=False)
    tag=serializers.SerializerMethodField(required=False)

    class Meta:
        model=Complain
        fields=['complain_id','comp_user_id','comped_user_id','comp_date',
                'category','comp_post_id','comp_comment_id','tag']
        
    #def get_tag(self,validated_data):
    #    if validated_data.get('')

    def validate(self, data):  #게시글, 댓글 중 1 신고 맞지? 확인
        comp_post_id = data.get('comp_post_id')
        comp_comment_id = data.get('comp_comment_id')
        comp_user=extract_user_from_jwt(self.context['request']) #신고자
        if (not comp_post_id) and (not comp_comment_id):
            raise serializers.ValidationError("게시글 또는 댓글을 지정해야 합니다.")
        # 게시글과 댓글이 동시에 지정된 경우 예외 처리
        if (comp_post_id is not None) and (comp_comment_id is not None):
            raise serializers.ValidationError("게시글과 댓글을 동시에 지정할 수 없습니다.")

        if comp_post_id:
            try:
                comped_post=Post.objects.get(post_id=comp_post_id) #영구삭제는 아닌데,
                if not comped_post.display: #display 가 False일때
                    raise serializers.ValidationError("이미 삭제된 게시글입니다.")
                if comped_post.author==comp_user:
                    raise serializers.ValidationError("자신의 게시글은 신고 할 수 없습니다.")
                if Complain.objects.filter(comp_post=comped_post,comp_user=comp_user).exists():
                    raise serializers.ValidationError('이미 신고한 게시글입니다.')
            except ObjectDoesNotExist: #영구삭제일 때
                raise serializers.ValidationError("이미 삭제된 게시글입니다.")
        if comp_comment_id:
            try:
                comped_comment=Comment.objects.get(comment_id=comp_comment_id) #영구삭제는 아닌데,
                if not comped_comment.display: #display 가 False일때
                    raise serializers.ValidationError("이미 삭제된 댓글입니다.")
                if comped_comment.writer==comp_user:
                    raise serializers.ValidationError("자신의 댓글은 신고 할 수 없습니다.")
                if Complain.objects.filter(comp_comment=comped_comment,comp_user=comp_user).exists():
                    raise serializers.ValidationError('이미 신고한 댓글입니다.')
            except ObjectDoesNotExist: #영구삭제일 때
                raise serializers.ValidationError("이미 삭제된 댓글입니다.")
        return data

    def create(self, validated_data):
        comp_post_id = validated_data.get('comp_post_id')
        comp_comment_id = validated_data.get('comp_comment_id')
        category = validated_data.get('category')

        # 게시글과 댓글 ID 중 하나가 있는 경우에만 해당 모델 "인스턴스"를 할당
        if comp_post_id: #게시글 신고일 때

            comp_post = Post.objects.get(post_id=comp_post_id)
            comp_comment=None
            tag="f{comp_post.board.board_name} 게시글"
            comped_user=comp_post.author

        elif comp_comment_id: #댓글 신고일 때
            comp_comment = Comment.objects.get(comment_id=comp_comment_id)
            comp_post=comp_comment.post
            tag="f{comp_post.board.board_name} 댓글"
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
'''
#신고 조회
class ComplainSerializer(serializers.ModelSerializer): 
    comp_post = PostSerializer(read_only=True)
    #comp_comment = CommentSerializer(read_only=True)
    comp_user = UserSerializer(read_only=True)
    comped_user = UserSerializer(read_only=True)

    class Meta:
        model = Complain
        fields = [
            'complain_id', #고유 uuid
            'comp_post_id', 인풋
            'comp_comment_id',  인풋
            'comp_user_id',알려줘야함
            'comped_user_id', 알려줘야함
            'comp_date',알려줘야함
            'category',알려줘야함
            'status',
        ]
        
#처리 상태
class ComplainStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complain
        fields = ['status']

'''