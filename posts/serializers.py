from rest_framework import serializers

from .models import Post, Image

#게시글 목록 조회 시리얼라이저
class PostListSerializer(serializers.ModelSerializer):
    #author_name = serializers.CharField(source=author.) #jwt 구현 코드 통해서 바꾸기 거기서 이름 가져오기
    cmter_size = serializers.IntegerField(source='cmter_size')
    like_size = serializers.IntegerField(source='like_size')

    class Meta:
        model = Post
        fields = ['title', 'content', 'like_size', 'cmter_size', 'created_at', 'author_name','anon_status']
    
#게시글 단일 조회 시리얼라이저
class PostDetailSerializer(serializers.ModelSerializer):
    #author_name = serializers.SerializerMethodField()
    #author_profile = serializers.SerializerMethodField() #프로필을 어떻게 처리해야 하는가? 그냥 author.profile 해서 가져와서 뿌려주고 프론트에서 익명이면 가리게?
    cmter_size = serializers.IntegerField(source='cmter_size')
    like_size = serializers.IntegerField(source='like_size')

    class Meta:
        model = Post
        fields = ['title', 'content', 'like_size', 'cmter_size', 'created_at', 'author_name', 'author_profile']

    def get_author_name(self, obj):
        return obj.author.username if not obj.anon_status else "익명"


#게시글 작성 시리얼라이저
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['imgfile']

class PostCreateSerializer(serializers.ModelSerializer):

    images = ImageSerializer(many=True, required=False)
    anon_status = serializers.BooleanField(required=False,default=False)

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