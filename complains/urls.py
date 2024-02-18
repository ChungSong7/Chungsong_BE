from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import ComplainView,FreezeView,TempView
urlpatterns = [
    path('', ComplainView.as_view(),name='Complian'), #신고리스트 조회, 신고 접수
    path('freeze/', FreezeView.as_view(),name='ComplianStatus'), #신고 처리(정지 or skip), 개인정지 이력은 users 로 접근.
    path('temp/',TempView.as_view(),name='Temp'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
