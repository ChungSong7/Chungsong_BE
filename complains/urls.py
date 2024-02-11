from django.urls import path
from .views import ComplainCreateAPIView, ComplainListAPIView

urlpatterns = [
    path('complains/create/', ComplainCreateAPIView.as_view(), name='complain-create'),
    path('complains/list/', ComplainListAPIView.as_view(), name='complain-list'),
]