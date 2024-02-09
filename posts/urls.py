from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import PostCreateView,PostDetailView


urlpatterns = [
    #path("",BoardView.as_view(),name='Board'),
    path('',PostCreateView.as_view(),name='PostCreate'),
    path('<uuid:post_id>/', PostDetailView.as_view(), name='PostDetail'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
