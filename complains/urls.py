from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import ComplainView,ComplainCheckView
urlpatterns = [
    path('', ComplainView.as_view(),name='Complian'), #신고리스트 조회, 신고 접수
    path('check/',ComplainCheckView.as_view(),name='ComplainCheck'), #신고접수 -> 처리완료 상태 바꾸기
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
