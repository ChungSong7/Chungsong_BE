from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import CommentView,CommentDetailView,CommentLikeView


urlpatterns = [
    path('', CommentView.as_view(), name='Comment'),
    path('<uuid:comment_id>/',CommentDetailView.as_view(),name='CommentDetail'),
    path('<uuid:comment_id>/like/',CommentLikeView.as_view(),name='CommentLike'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
