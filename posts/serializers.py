from rest_framework import serializers
from django.shortcuts import get_object_or_404
from users.authentications import extract_user_from_jwt

from boards.models import Board
from .models import Post, Image,Comment,Commenter

import os
import random

#게시글 작성, 조회 시리얼라이저
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['imgfile']

class PostSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, read_only=True)

    author_name=serializers.SerializerMethodField(required=False)
    anon_status = serializers.BooleanField(required=True)
    board= serializers.CharField(source='board.board_name',required=False) #아니면 board_id로 줘야함
    board_id=serializers.UUIDField(source='board.board_id',required=False)
    author_id=serializers.UUIDField(source='author.user_id',required=False)
    
    def get_images(self, obj):
        return ImageSerializer(instance=obj.images.all(), many=True, context=self.context).data
    #return ImageSerializer(instance=self.imgfile, many=True, context=self.context).data
    
    def get_author_name(self, obj):#익명 여부에 따라 별명 or 익명
        if obj.author==None or obj.author.status=='탈퇴회원':
            return "탈퇴회원"
        return obj.author.username if not obj.anon_status else "익명"
    
    def validate(self, data):
        # 이미지 유효성 검사
        images_data = self.context['request'].FILES.getlist('images')
        if len(images_data) > 10:
            raise serializers.ValidationError({"message": '이미지는 최대 10개까지 업로드할 수 있습니다.'})
        for image_data in images_data:
            if not image_data.content_type.startswith('image'):
                raise serializers.ValidationError({'message':'이미지 파일이 아닙니다.'})
            if image_data.size > (5 * 1024 * 1024):  # 5MB 제한
                raise serializers.ValidationError({'message':'이미지 파일 크기는 최대 5MB입니다.'})
        return data
    
    class Meta:
        model = Post
        
        fields = ['post_id','author_id','title', 'content', 'like_size', 'comment_size', 'created_at', 
                'board','board_id','author_profile','author_name','anon_status','images']
    
    def create(self, validated_data):

        board_id = self.context['board_id']    
        board = get_object_or_404(Board, board_id=board_id)
        user = extract_user_from_jwt(self.context['request'])

        images_data=validated_data.pop('images', None)

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
        # 이미지 생성
        image_set = self.context['request'].FILES
        for image_data in image_set.getlist('images'):
            Image.objects.create(post=post, imgfile=image_data)

        
        return post
    
