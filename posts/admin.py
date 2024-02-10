from django.contrib import admin
from .models import Post,Image,Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['board','post_id','title','content','created_at','author','author_profile',
                    'anon_status','comment_size','like_size','warn_size','display']
    
@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display=['post','id','imgfile']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['comment_id', 'post', 'content', 'created_at', 'anon_status',
                'commenter', 'like_size', 'warn_size','display']