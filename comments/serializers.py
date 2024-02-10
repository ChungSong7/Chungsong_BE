from rest_framework import serializers
from django.shortcuts import get_object_or_404
from users.authentications import extract_user_from_jwt

from posts.models import Post,Comment

class CommentSerializer(serializers.ModelSerializer):
    anon_status = serializers.BooleanField(required=True)
    commenter_profile=serializers.IntegerField(required=False) 
    post= serializers.UUIDField(required=False)
    commenter= serializers.CharField(required=False)

    class Meta:
        model = Comment
        fields = ['comment_id', 'post', 'content', 'created_at', 'anon_status',
                'commenter', 'like_size', 'warn_size','display','commenter_profile']
        #'anon_status', 'anon_num',

    def create(self, validated_data):
        #images_data = validated_data.pop('images', None)
        post_id = self.context['post_id'] #url에 담겨있
        post = get_object_or_404(Post, post_id=post_id)

        comment_data = {
            'post': post, #게시판 객체.이름
            'content': validated_data['content'],
            'commenter': self.context['commenter'], #별명? 아님 익명2?
            'anon_status': validated_data.get('anon_status'),
        }
        # 댓글 생성
        comment = Comment.objects.create(**comment_data)

        #post 댓글 수 ++
        post.comment_size = Comment.objects.filter(post=post, display=True).count()
        post.save()
        
        return comment