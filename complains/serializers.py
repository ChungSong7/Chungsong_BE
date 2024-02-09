from rest_framework import serializers
from .models import Complain

from users.serializers import UserSerializer
#from posts.serializers import PostSerializer
#from comment.serializers import CommentSerializer

class ComplainSerializer(serializers.ModelSerializer):
    #comp_post = PostSerializer(read_only=True)
    #comp_comment = CommentSerializer(read_only=True)
    comped_user = UserSerializer(read_only=True)

    class Meta:
        model = Complain
        fields = ['complain_id','comp_post','comp_comment','comp_user','comped_user','comp_date','category','status']

