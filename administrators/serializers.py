from rest_framework import serializers
from users.authentications import extract_user_from_jwt
from .models import RoomRequest,FreezeHistory
from users.models import User
from django.shortcuts import get_object_or_404
class RoomRequestSerializer(serializers.ModelSerializer):
    user= serializers.UUIDField(required=False)
    nickname= serializers.CharField(source='user.nickname',required=False)
    user_id=serializers.CharField(source='user.user_id',required=False)
    class Meta:
        model = RoomRequest
        fields = ['room_request_id','user','user_id', 'pre_room', 'new_room', 'request_date', 'status','nickname']
        read_only_fields = ['request_date', 'status']
    def validate(self,data):
        pre_room=data.get('pre_room')
        new_room=data.get('new_room')
        if pre_room and new_room:
            if pre_room==new_room:
                raise serializers.ValidationError("기존의 방과 다른 방을 입력해주세요.")
        return data
    
    def create(self, validated_data):
            user=get_object_or_404(User,user_id=validated_data['user'])
            roomrequest_data = {
            'user':user, #댓글 작성자 FK
            'pre_room': validated_data['pre_room'],
            'new_room': validated_data['new_room'], #별명? 아님 익명2?
        }
            instance = RoomRequest.objects.create(**roomrequest_data)
            return instance
    
    def update(self, instance, validated_data):
        instance.new_room = validated_data.get('new_room')
        instance.status = 1  # 처리 완료 상태로 변경
        instance.save()
        return instance
    

class FrozenHistorySerializer(serializers.ModelSerializer):
    user_id=serializers.CharField(source='user.user_id',required=False)
    class Meta:
        model = FreezeHistory
        fields = ['freeze_history_id','user','user_id','complained_size','start_date','end_date','days']