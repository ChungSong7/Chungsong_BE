from django.contrib import admin
from posts.models import Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['comment_id', 'post', 'up_comment_id','content', 'created_at', 'anon_status','writer',
                'commenter', 'like_size', 'warn_size','display']