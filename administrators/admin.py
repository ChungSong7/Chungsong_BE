from django.contrib import admin
from .models import RoomRequest,FreezeHistory

@admin.register(RoomRequest)
class RoomRequestAdmin(admin.ModelAdmin):
    list_display = ['room_request_id', 'user', 'pre_room', 'new_room', 'request_date', 'status']

@admin.register(FreezeHistory)
class FreezeHistoryAdmin(admin.ModelAdmin):
    list_display = ['freeze_history_id','user','complained_size','start_date','end_date','days']