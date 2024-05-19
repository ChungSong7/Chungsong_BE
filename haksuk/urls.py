from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from haksuk.views import MenuView,TestView
urlpatterns = [
    path('menu/', MenuView.as_view(),name='Menu'), #식단조회
    path('test/',TestView.as_view(),name='Test'), #DB 통신 테스트
]