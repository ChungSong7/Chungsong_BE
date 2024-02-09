from django.contrib import admin
from .models import Post,Image

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['board','post_id','title','content','created_at','author','author_profile',
                    'anon_status','cmter_size','like_size','warn_size','display']
    
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display=['post','id','imgfile']