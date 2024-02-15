from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import ComplainAPI,ComplainCreateAPI,ComplainStatusAPI,ComplainListAPI

urlpatterns = [
    path('list/', ComplainListAPI.as_view(),name='Complians'),
    path('list/<int:complain_id>', ComplainAPI.as_view(),name='Complain'),
    path('create/', ComplainCreateAPI.as_view(),name='ComplianCrate'),
    path('status', ComplainStatusAPI.as_view(),name='ComplianStatus'),
    
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
