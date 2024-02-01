from rest_framework import serializers

from .models import Post, Image


#게시글 목록 조회 & 단일 조회 회종
class PostSerializer(serializers.ModelSerializer):
    author_nickname = serializers.CharField(source='author.nickname')

    class Meta:
        model = Post
        field = ['title','content','like_size','cmter_size','create_at','author_nickname','anon_status']


#게시글 작성 시리얼라이저
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['imgfile']

class PostCreateSerializer(serializers.ModelSerializer):
    images = ImageSerializer(many=True, required=False)

    class Meta:
        model = Post
        fields = ['title', 'content','images', 'anon_status']
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', None)
        post = Post.objects.create(**validated_data)
        if images_data:
            for image_data in images_data:
                Image.objects.create(post=post, **image_data)
        return post