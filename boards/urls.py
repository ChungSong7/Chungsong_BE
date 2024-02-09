from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import BoardView,BoardPostsView

urlpatterns = [
    path('',BoardView.as_view(),name='Board'),
    path('<int:board_id>/',BoardPostsView.as_view(),name='BoardPosts'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
