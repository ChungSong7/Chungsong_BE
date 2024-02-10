from rest_framework import serializers
from django.shortcuts import get_object_or_404
from users.authentications import extract_user_from_jwt

from boards.models import Board
from .models import Post, Image,Comment,Commenter

import random

#게시글 작성, 조회 시리얼라이저
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['imgfile']
#게시글 작성, 조회 시리얼라이저
class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)
    author_name=serializers.SerializerMethodField(required=False)
    anon_status = serializers.BooleanField(required=True)
    board= serializers.CharField(source='board.board_name',required=False) #아니면 board_id로 줘야함

    class Meta:
        model = Post
        
        fields = ['post_id','title', 'content', 'like_size', 'cmter_size', 'created_at', 
                'board','author_profile','author_name','anon_status','images']
    def get_author_name(self, obj): #익명 여부에 따라 별명 or 익명
        return obj.author.username if not obj.anon_status else "익명"
    
    def create(self, validated_data):
        #images_data = validated_data.pop('images', None)
        board_id = self.context['board_id']
        board = get_object_or_404(Board, board_id=board_id)
        user = extract_user_from_jwt(self.context['request'])

        # 익명 여부에 따라 작성자 프로필 설정
        anon_status = validated_data.get('anon_status')
        if anon_status:
            author_profile = random.randint(1, 8) 
        else:
            author_profile = user.profile_image # 1부터 8까지의 랜덤 정수
        
        post_data = {
            'board': board, #게시판 객체.이름
            'title': validated_data['title'],
            'content': validated_data['content'],
            'author': user, #유저객체.uuid
            'author_profile': author_profile,
            'anon_status': anon_status,
        }
        # 게시글 생성
        post = Post.objects.create(**post_data)
        # 이미지가 있는 경우 처리
        pictures_data = validated_data.get('images')
        if pictures_data:
            for picture_data in pictures_data:
                Image.objects.create(post=post, **picture_data)
        
        return post
    
