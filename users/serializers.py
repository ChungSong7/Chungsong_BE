import re
from rest_framework import serializers
from .models import User

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
        if len(password) < 10:
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