from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import PostCreateView,PostDetailView,CommentView,CommentDetailView


urlpatterns = [
    #path("",BoardView.as_view(),name='Board'),
    path('',PostCreateView.as_view(),name='PostCreate'),
    path('<uuid:post_id>/', PostDetailView.as_view(), name='PostDetail'),
    path('<uuid:post_id>/comments/', CommentView.as_view(), name='Comment'),
    path('<uuid:post_id>/comments/<uuid:comment_id>/',CommentDetailView.as_view(),name='CommentDetail'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
