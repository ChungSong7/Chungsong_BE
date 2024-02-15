from rest_framework import serializers
from users.authentications import extract_user_from_jwt
from .models import RoomRequest

class RoomRequestSerializer(serializers.ModelSerializer):
    user= serializers.CharField(source='user.username',required=False)
    nickname= serializers.CharField(source='user.nickname',required=False)

    class Meta:
        model = RoomRequest
        fields = ['room_request_id','user', 'pre_room', 'new_room', 'request_date', 'status','nickname']
        read_only_fields = ['request_date', 'status']
    def validate(self,data):
        pre_room=data.get('pre_room')
        new_room=data.get('new_room')
        if pre_room and new_room:
            if pre_room==new_room:
                raise serializers.ValidationError("기존의 방과 다른 방을 입력해주세요.")
        return data
    
    def create(self, validated_data):
            instance = RoomRequest.objects.create(**validated_data)
            return instance
    
    def update(self, instance, validated_data):
        instance.new_room = validated_data.get('new_room')
        instance.status = 1  # 처리 완료 상태로 변경
        print(instance.user)
        print(type(instance.user))
        instance.save()
        return instance
    '''
    def update(self, instance, validated_data):
        validated_data['status']=1
        instance.new_room = validated_data.get('new_room')
        instance.save()
        return instance
    
    '''