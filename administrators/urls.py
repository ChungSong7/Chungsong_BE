from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import NewUserView,RoomRequestView,FreezeView,AdminDeleteView,SchoolListView,SchoolBoardListView,UseridInfoView

urlpatterns = [
    path('new_user/', NewUserView.as_view(), name='NewUser'),
    path('room_request/',RoomRequestView.as_view(),name='RoomRequest'),
    path('freeze/', FreezeView.as_view(),name='Freeze'), #유저 정지먹이기
    path('freeze/<uuid:user_id>/',FreezeView.as_view(),name='FrozenHistory'), #유저별 정지이력
    path('delete/',AdminDeleteView.as_view(),name='AdminDelete'), #휴지통 조회, 휴지통삭제
    path('school_list/',SchoolListView.as_view(),name='SchoolList'),#학교 리스트
    path('school_boards/',SchoolBoardListView.as_view(),name='SchoolBoardList'),#학교별 게시판 list up
    path('userid_info/',UseridInfoView.as_view(),name='UseridInfo')#useer_id로 회원정보 조회 (관리자용)
]

# 이미지 경로 추가
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


