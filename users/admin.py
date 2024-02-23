from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,DeletedUser,EmailVarify,Notice

class CustomUserAdmin(UserAdmin):
    # 유저 리스트에 보여질 필드 지정
    list_display = ('user_id','username', 'nickname','email','room','room_card','school',
                    'created_at','status','suspension_end_date','complained','profile_image') 

admin.site.register(User, CustomUserAdmin)

@admin.register(DeletedUser)
class PostAdmin(admin.ModelAdmin):
    list_display = ['deleted_user_id','name','email','room','school']

@admin.register(EmailVarify)
class EmailVarifyAdmin(admin.ModelAdmin):
    list_display = ['email_varify_id','email','code','created_at']


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display=['notice_id','user','root_id','category','created_at','checked']