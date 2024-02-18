from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

class CustomUserAdmin(UserAdmin):
    # 유저 리스트에 보여질 필드 지정
    list_display = ('user_id','username', 'nickname','email','room','room_card','school',
                    'status','suspension_end_date','complained','profile_image') 

admin.site.register(User, CustomUserAdmin)