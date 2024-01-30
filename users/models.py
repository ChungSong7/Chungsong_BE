from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    user_id=models.UUIDField(verbose_name='고유번호',primary_key=True, default=uuid.uuid4, unique=True,editable=False)
    nickname=models.CharField(verbose_name='닉네임', max_length=255,unique=True)
    room=models.PositiveSmallIntegerField(verbose_name='호실수')
    email=models.EmailField(verbose_name='이메일',max_length=255,unique=True)
    password=models.CharField(verbose_name='비밀번호',max_length=255)
    username=models.CharField(verbose_name='이름', max_length=255)
    school=models.CharField(verbose_name='학교',max_length=255)
    room_card=models.ImageField(verbose_name='호실카드 사진')
    profile_image=models.IntegerField(verbose_name='프로필 캐릭터',default=0)
    complained=models.IntegerField(verbose_name='피신고수',default=0)
    STATUS_CHOICE=('인증대기','사생인증','정지','학생회','관리자')
    status=models.CharField(verbose_name='사용자 권한',max_length=255,default=STATUS_CHOICE[0])
    
    USERNAME_FIELD='email' #email로 로그인할거니까! 
    REQUIRED_FIELDS=['nickname', 'room','username','school','room_card','profile_image']