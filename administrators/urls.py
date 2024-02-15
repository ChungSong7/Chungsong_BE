from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import NewUserView,RoomRequestView

urlpatterns = [
    path('new_user/', NewUserView.as_view(), name='NewUser'),
    path('room_request/',RoomRequestView.as_view(),name='RoomRequest'),
]

# 이미지 경로 추가
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


