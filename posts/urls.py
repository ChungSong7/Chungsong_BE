from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from .views import PostCreateView,PostView,PostLikeView


urlpatterns = [
    #path("",BoardView.as_view(),name='Board'),
    path('',PostCreateView.as_view(),name='PostCreate'),
    path('<uuid:post_id>/', PostView.as_view(), name='PostDetail'),
    path('<uuid:post_id>/like/', PostLikeView.as_view(), name='PostLike'),
    path('<uuid:post_id>/comments/',include('comments.urls')),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

