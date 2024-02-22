import re
from rest_framework import serializers
from .models import User,Notice
from django.contrib.auth.hashers import make_password,check_password
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from administrators.models import FreezeHistory
from posts.models import Comment,Post


class UserSerializer(serializers.ModelSerializer):
    password_confirm=serializers.CharField(write_only=True)
    class Meta:
        model=User
        fields=['user_id','username','nickname','email','room','room_card','school',
                'password','password_confirm','status','complained','profile_image']
        extra_kwargs={
            'password':{'write_only':True}, #비번 필드는 읽기 전용
        }
    
    #계정 생성 전 비밀번호(password) 유효성 검사
    def validate(self, data):
        print(data)
        password=data.get('password')
        password_confirm=data.get('password_confirm')

        # 비밀번호의 길이가 10자 이상인지 확인
        if len(password) < 10 or len(password_confirm)<10:
            raise serializers.ValidationError("비밀번호는 10자 이상이어야 합니다.")
        
        # 영문, 숫자, 특수문자가 각각 한 개 이상씩 포함되어 있는지 확인
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{10,}$', password):
            raise serializers.ValidationError("비밀번호는 영문, 숫자, 특수문자를 각각 한 개 이상 포함하여야 합니다.")
        
        #비밀번호, 비밀번호 확인 일치 검사
        if password != password_confirm:
            raise serializers.ValidationError("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
        

        return data

    #계정 생성 def
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        instance = User.objects.create(**validated_data)
        instance.set_password(validated_data['password']) #비밀번호 해싱
        instance.save()
        return instance


class UserExistenceCheckSerializer(serializers.Serializer):
    username = serializers.CharField()
    room = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, data):
        username = data.get('username')
        room = data.get('room')
        email = data.get('email')

        # 해당하는 유저가 있는지 확인
        user = get_object_or_404(User, username=username, room=room, email=email)

        # 유저가 존재한다면 User 객체 반환
        return user
    


class UserUpdateSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=False)
    password_confirm = serializers.CharField(write_only=True, required=False)
    new_email = serializers.EmailField(required=False)
    username=serializers.CharField(required=True)
    room=serializers.IntegerField(required=True)
    email=serializers.EmailField(required=True)

    def validate(self, data):
        #유저있지?
        serializer = UserExistenceCheckSerializer(data=data)
        if not serializer.is_valid():
            raise serializers.ValidationError("User does not exist")
        user = serializer.validated_data

        new_email = data.get('new_email')
        password = data.get('password')
        password_confirm = data.get('password_confirm')

        if new_email and password:
            raise serializers.ValidationError("email, password 하나만 입력하세요(근데 이거 일어날 일 X 예외)")
        elif new_email:
            # 이메일 변경 요청일 때 유효성 검사
            if User.objects.filter(email=new_email).exists():
                raise serializers.ValidationError("입력한 이메일은 이미 사용 중입니다. 다른 이메일을 입력해주세요.")
            if new_email and user.email == new_email:
                raise serializers.ValidationError("새 이메일은 현재 이메일과 다르게 입력해야 합니다.")
        elif password and password_confirm:
            # 비밀번호 변경 요청일 때 유효성 검사
            if len(password) < 10 or len(password_confirm) < 10:
                raise serializers.ValidationError("비밀번호는 10자 이상이어야 합니다.")
            if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{10,}$', password):
                raise serializers.ValidationError("비밀번호는 영문, 숫자, 특수문자를 각각 한 개 이상 포함하여야 합니다.")
            if password != password_confirm:
                raise serializers.ValidationError("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
            if check_password(password,user.password):
                raise serializers.ValidationError("기존 비밀번호와 다른 비밀번호를 입력하세요.")
        else: 
            raise serializers.ValidationError('입력 조건이 맞지 않습니다.')
        return data

    def update(self, instance, validated_data):
        new_email = validated_data.get('new_email')
        password = validated_data.get('password')
        
        if new_email:
            instance.email = new_email
            instance.save()
            return Response({"message": "Email updated successfully."}, status=status.HTTP_200_OK)
        elif password:
            instance.set_password(password)
            instance.save()
            return Response({"message": "password updated successfully."}, status=status.HTTP_200_OK)
        
class NoticeSerializer(serializers.ModelSerializer):
    message=serializers.SerializerMethodField() #카테고리에 따라
    content=serializers.SerializerMethodField() #그 구체적 댓or 내용
    notice_title=serializers.SerializerMethodField() #자유게시판 or 정지 

    comment_id = serializers.SerializerMethodField(required=False,allow_null=True)
    post_id = serializers.SerializerMethodField(required=False,allow_null=True)

    class Meta:
        model=Notice
        fields=['notice_id','user','category','noticed_at','checked', #'root_id'
                'message','content','notice_title','post_id','comment_id']
        
    def get_message(self, instance):
        if instance.category == '댓글':
            return "내가 쓴 글에 댓글이 달렸어요!"
        elif instance.category == '대댓글':
            return "내가 쓴 댓글에 대댓글이 달렸어요!"
        elif instance.category == '정지':
            freeze=get_object_or_404(FreezeHistory,freeze_history_id=instance.root_id)
            return f"{freeze.days}일 정지 처분을 받았습니다. {freeze.days}일 동안 게시글 및 댓글을 작성할 수 없습니다."
        elif instance.category== '웅성웅성':
            return "내가 쓴 글이 웅성웅성에 들어갔어요!"
        else:
            return "알림 카테고리가 잘못되어 메세지를 생성할 수 없습니다."
    
    def get_content(self,instance):
        if instance.category=='댓글':
            comment=get_object_or_404(Comment,comment_id=instance.root_id)
            return comment.content
        elif instance.category=='대댓글':
            comment=get_object_or_404(Comment,comment_id=instance.root_id)
            return comment.content
        elif instance.category == '정지':
            return None
        elif instance.category=='웅성웅성':
            post=get_object_or_404(Post,post_id=instance.root_id)
            return post.title
        else:
            return None
    
    def get_notice_title(self,instance):
        if instance.category=='댓글':
            comment=get_object_or_404(Comment,comment_id=instance.root_id)
            return comment.post.board.board_name
        if instance.category=='대댓글':
            comment=get_object_or_404(Comment,comment_id=instance.root_id)
            return comment.post.board.board_name
        elif instance.category == '정지':
            return '정지 처분'
        elif instance.category=='웅성웅성':
            post=get_object_or_404(Post,post_id=instance.root_id)
            return post.board.board_name
        else:
            return None
    def get_comment_id(self,instance):
        if instance.category=='댓글':
            comment=get_object_or_404(Comment,comment_id=instance.root_id)
            return comment.comment_id
        elif instance.category=='대댓글':
            comment=get_object_or_404(Comment,comment_id=instance.root_id)
            return comment.comment_id
        elif instance.category == '정지':
            return None
        else:
            return None
    def get_post_id(self,instance):
        if instance.category=='댓글':
            comment=get_object_or_404(Comment,comment_id=instance.root_id)
            return comment.post.post_id
        elif instance.category=='대댓글':
            comment=get_object_or_404(Comment,comment_id=instance.root_id)
            return comment.comment_id
        elif instance.category == '정지':
            return None
        elif instance.category=='웅성웅성':
            post=get_object_or_404(Post,post_id=instance.root_id)
            return post.post_id
        else:
            return None
        
        #'content': comment.content,  # 댓글 내용
            #'notice_title':post.board.board_name,
            #'comment_id':comment.comment_id,
            #'post_id':post.post_id,