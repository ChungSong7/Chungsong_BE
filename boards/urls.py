from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from .views import BoardView,BoardPostsView,HotPostView,MySchoolBoardView,health_check

urlpatterns = [
    path('',BoardView.as_view(),name='Board'),
    path('<int:board_id>/',BoardPostsView.as_view(),name='BoardPosts'),
    path('<int:board_id>/posts/',include('posts.urls')),
    path('hot_posts/',HotPostView.as_view(),name='HotPost'),
    path('my_school_board/',MySchoolBoardView.as_view(),name='MySchoolBoard'),
    path('health_check/',health_check,name='HealthCheck'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)