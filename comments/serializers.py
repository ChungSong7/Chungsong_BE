from rest_framework import serializers
from django.shortcuts import get_object_or_404
from users.authentications import extract_user_from_jwt

from users.serializers import NoticeSerializer
from posts.models import Post,Comment
from users.models import Notice
class CommentSerializer(serializers.ModelSerializer):
    anon_status = serializers.BooleanField(required=True)
    commenter_profile=serializers.IntegerField(required=False) 
    post= serializers.UUIDField(required=False)
    commenter= serializers.CharField(required=False)
    writer_id=serializers.UUIDField(source='writer.user_id',required=False)

    class Meta:
        model = Comment
        fields = ['comment_id', 'post','up_comment_id', 'content', 'created_at', 'anon_status','writer_id',
                'commenter', 'like_size', 'warn_size','display','commenter_profile']
        #'anon_status', 'anon_num',

    def create(self, validated_data):
        #images_data = validated_data.pop('images', None)
        post_id = self.context['post_id'] #url에 담겨있
        post = get_object_or_404(Post, post_id=post_id)
        user=extract_user_from_jwt(self.context['request'])

        comment_data = {
            'post': post, #게시판 객체.이름
            'up_comment_id':self.context['up_comment_id'], #어미 댓글
            'writer':user, #댓글 작성자 FK
            'content': validated_data['content'],
            'commenter': self.context['commenter'], #별명? 아님 익명2?
            'anon_status': validated_data.get('anon_status'),
        }
        # 댓글 생성
        comment = Comment.objects.create(**comment_data)
        
        #post 댓글 수 ++
        post.comment_size = Comment.objects.filter(post=post, display=True).count()
        post.save()

        #게시글 주인 아닌데 댓글을 달았다:: 게시글 주인한테 알림 생성
        if comment.writer!=post.author:
            notice_data = {
                'user': post.author,  # 게시글 작성자
                'root_id': comment.comment_id,  # 댓글의 고유 ID
                'category': '댓글',  # 알림 카테고리
            }
            Notice.objects.create(**notice_data)
        #어미댓글 있는데 나 아니면, 어미댓 주인한테 알림.
        if comment.up_comment_id:
            up_comment=get_object_or_404(Comment,comment_id=comment.up_comment_id)
            if comment.writer != up_comment.writer:
                notice_data={
                    'user':up_comment.writer, #어미댓 작성자
                    'root_id':comment.comment_id, #대댓글 고유 ID
                    'category':'대댓글', #알림 카테고리
                }
                Notice.objects.create(**notice_data)
        return comment