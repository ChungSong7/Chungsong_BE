from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from .views import BoardView,BoardPostsView

urlpatterns = [
    path('',BoardView.as_view(),name='Board'),
    path('<int:board_id>/',BoardPostsView.as_view(),name='BoardPosts'),
    path('<int:board_id>/posts/',include('posts.urls')),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
