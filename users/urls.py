from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import SignupView,LoginView,UserInfoView,LogoutView,RefreshJWTTokenView,NickDupCheckView

urlpatterns = [
    path('signup/', SignupView.as_view(),name='SignUp'),
    path('login/',LoginView.as_view(),name='Login'),
    path('user_info/',UserInfoView.as_view(),name='UserInfo'),
    path('refresh_jwt_token/',RefreshJWTTokenView.as_view(),name='RefreshJWTToken'),
    path('logout/',LogoutView.as_view(),name='Logout'),
    path('signup/nkname_dupcheck/',NickDupCheckView.as_view(),name='NickDupCheck'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
