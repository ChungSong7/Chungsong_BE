from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from haksuk.views import MenuView
urlpatterns = [
    path('menu/', MenuView.as_view(),name='Menu'), #식단조회
]
