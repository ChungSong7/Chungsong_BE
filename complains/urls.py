from django.urls import path
from .views import ComplainCreateAPIView, ComplainListAPIView

urlpatterns = [
    path('create/', ComplainCreateAPIView.as_view(), name='ComplainCreate'),
    path('list/', ComplainListAPIView.as_view(), name='ComplainList'),
]