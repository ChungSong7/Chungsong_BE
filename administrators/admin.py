from django.contrib import admin
from .models import RoomRequest,FreezeHistory

@admin.register(RoomRequest)
class RoomRequestAdmin(admin.ModelAdmin):
    list_display = ['room_request_id', 'user', 'pre_room', 'new_room', 'created_at', 'status']

@admin.register(FreezeHistory)
class FreezeHistoryAdmin(admin.ModelAdmin):
    list_display = ['freeze_history_id','user','complained_size','created_at','end_date','days']