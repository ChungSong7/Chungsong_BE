from django.contrib import admin
from .models import Complain

@admin.register(Complain)
class ComplainAdmin(admin.ModelAdmin):
    list_display = ['complain_id','category','comp_post','comp_comment',
                    'comp_user','comped_user','created_at','status']
