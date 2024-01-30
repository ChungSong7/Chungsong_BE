from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import SignupView,LoginView,UserInfoView,LogoutView,RefreshTokenView

urlpatterns = [
    path('signup/', SignupView.as_view(),name='SignUp'),
    path('login/',LoginView.as_view(),name='Login'),
    path('info/',UserInfoView.as_view(),name='UserInfo'),
    path('refresh_token/',RefreshTokenView.as_view(),name='RefreshToken'),
    path('logout/',LogoutView.as_view(),name='Logout'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
