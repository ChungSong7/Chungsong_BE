from django.contrib import admin
from .models import RoomRequest

@admin.register(RoomRequest)
class RoomRequestAdmin(admin.ModelAdmin):
    list_display = ['room_request_id', 'user', 'pre_room', 'new_room', 'request_date', 'status']
