from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import SignupView,LoginView,UserInfoView,LogoutView,RefreshJWTTokenView,NickDupCheckView,UserMatchingView
from .views import MyPostView,MyCommentView,SendEmailCodeView,CheckEmailCodeView
urlpatterns = [
    path('signup/', SignupView.as_view(),name='SignUp'),
    path('login/',LoginView.as_view(),name='Login'),
    path('user_info/',UserInfoView.as_view(),name='UserInfo'),
    path('refresh_jwt_token/',RefreshJWTTokenView.as_view(),name='RefreshJWTToken'),
    path('logout/',LogoutView.as_view(),name='Logout'),
    path('signup/nkname_dupcheck/',NickDupCheckView.as_view(),name='NickDupCheck'),
    path('user_matching/',UserMatchingView.as_view(),name='UserMatching'),
    path('my_posts/',MyPostView.as_view(),name='MyPost'),
    path('my_comments/',MyCommentView.as_view(), name='MyComment'),
    path('send_emailcode/',SendEmailCodeView.as_view(),name='SendEmailCode'),
    path('check_emailcode/',CheckEmailCodeView.as_view(),name='CheckEmailCode'),
] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

