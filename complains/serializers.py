from rest_framework import serializers
from .models import Complain

from users.serializers import UserSerializer
from posts.serializers import PostDetailSerializer
#from comment.serializers import CommentSerializer


#신고 조회
class ComplainSerializer(serializers.ModelSerializer): 
    comp_post = PostDetailSerializer(read_only=True)
    #comp_comment = CommentSerializer(read_only=True)
    comp_user = UserSerializer(read_only=True)
    comped_user = UserSerializer(read_only=True)

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

#신고 작성
class ComplainCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complain
        fields = ['comp_post','comp_comment','comp_user','comped_user','category']

        def validate(self, data):
            return data

        def create(self, validated_data):
            complain = Complain.objects.create(**validated_data)

            comp_post = validated_data.get('comp_post')
            if comp_post:
                comp_post.warn_size += 1
                comp_post.save()
            
            comp_comment = validated_data.get('comp_comment')
            if comp_comment:
                comp_comment.warn_size += 1
                comp_comment.save()

            comped_user = validated_data.get('comped_user')
            if comped_user:
                comped_user.complained += 1
                comped_user.save()

            return complain
        
#처리 상태
class ComplainStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complain
        fields = ['status']

