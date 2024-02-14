from rest_framework import serializers
from .models import Complain

from users.serializers import UserSerializer
from posts.serializers import PostSerializer
from comments.serializers import CommentSerializer


class ComplainSerializer(serializers.ModelSerializer):
    
    comp_user_id = serializers.IntegerField(source='comp_user.id', read_only=True)
    comped_user_id = serializers.IntegerField(source='comped_user.id', read_only=True)
    comp_post_id = serializers.IntegerField(source='comp_post.id', required=False, allow_null=True)
    comp_comment_id = serializers.IntegerField(source='comp_comment.id', required=False, allow_null=True)

    class Meta:
        model = Complain
        fields = [
            'complain_id',
            'comp_post_id', 
            'comp_comment_id',  
            'comp_user_id',
            'comped_user_id', 
            'comp_date',
            'category',
            'status',
        ]

