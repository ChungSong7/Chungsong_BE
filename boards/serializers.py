from rest_framework import serializers

from .models import Board

#게시판 list 조회 시리얼라이저
class BoardSerializer(serializers.ModelSerializer):
    class Meta:
        model=Board
        fields = ['board_id', 'board_name']