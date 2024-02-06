import re
from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password,check_password
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status


class UserSerializer(serializers.ModelSerializer):
    password_confirm=serializers.CharField(write_only=True)
    class Meta:
        model=User
        fields=['user_id','username','nickname','email','room','room_card','school','password','password_confirm','status','complained','profile_image']
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
        if new_email:
            # 이메일 변경 요청일 때 유효성 검사
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
            if make_password(password) == user.password:
                raise serializers.ValidationError("기존 비밀번호와 다른 비밀번호를 입력하세요.")

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