from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid

class User(AbstractUser):
    user_id=models.UUIDField(verbose_name='고유번호',primary_key=True, default=uuid.uuid4, unique=True,editable=False)
    nickname=models.CharField(verbose_name='닉네임', max_length=255)
    room=models.PositiveSmallIntegerField(verbose_name='호실수')
    email=models.EmailField(verbose_name='이메일',max_length=255,unique=True)
    password=models.CharField(verbose_name='비밀번호',max_length=255)
    username=models.CharField(verbose_name='이름', max_length=255)
    school=models.CharField(verbose_name='학교',max_length=255)
    room_card=models.ImageField(verbose_name='호실카드 사진')
    profile_image=models.IntegerField(verbose_name='프로필 캐릭터',default=0)
    created_at=models.DateTimeField(verbose_name='가입 날짜',default=timezone.now)
    complained=models.IntegerField(verbose_name='피신고수',default=0)
    STATUS_CHOICES=[('인증대기','인증대기'),
                    ('사생인증','사생인증'),
                    ('정지','정지'),
                    ('학생회','학생회'),
                    ('관리자','관리자'),
                    ('탈퇴회원','탈퇴회원')]
    status=models.CharField(verbose_name='사용자 권한',max_length=255,default='인증대기')
    suspension_end_date = models.DateTimeField(verbose_name='정지 종료일', blank=True, null=True,default=None)

    def update_status(self):
        # 정지 상태인 경우 정지 종료일이 지났는지 확인하여 상태를 업데이트
        if self.status == '정지' and self.suspension_end_date is not None:
            if self.suspension_end_date <= timezone.now():
                self.status = '사생인증'  # 정지 종료일이 지나면 상태를 '사생인증'으로 변경
                self.save()
        

    
    USERNAME_FIELD='email' #email로 로그인할거니까! 
    REQUIRED_FIELDS=['nickname', 'room','username','school','room_card','profile_image']


class DeletedUser(models.Model):
    deleted_user_id=models.UUIDField(verbose_name='고유번호',primary_key=True, default=uuid.uuid4, unique=True,editable=False)
    name=models.CharField(verbose_name='이름',max_length=30)
    email=models.EmailField(verbose_name='이메일',max_length=255)
    room=models.PositiveSmallIntegerField(verbose_name='호실수')
    school=models.CharField(verbose_name='학교',max_length=255)
    #deleted_date=models.DateTimeField(verbose_name='탈퇴날짜',auto_now_add=True)##이거 추가해서 다시 마이그레이션해보자. 디비 싹 갈고^^

class EmailVarify(models.Model):
    email_varify_id=models.UUIDField(verbose_name='고유번호',primary_key=True, default=uuid.uuid4, unique=True,editable=False)
    email=models.EmailField(verbose_name='이메일',max_length=255,unique=True)
    code=models.CharField(verbose_name='인증번호',max_length=6)
    created_at=models.DateTimeField(verbose_name='인증코드 생성시간',auto_now_add=True)

class Notice(models.Model):
    notice_id=models.UUIDField(verbose_name='고유번호',primary_key=True, default=uuid.uuid4,unique=True,editable=False)
    user=models.ForeignKey(User,verbose_name='사용자',on_delete=models.CASCADE,related_name='notices')
    root_id=models.UUIDField(verbose_name='루트 객체 uuid')
    category=models.CharField(verbose_name='알림 카테고리',max_length=30)#웅성웅성, 댓글, 대댓글, 정지
    created_at=models.DateTimeField(verbose_name='알림 날짜',auto_now_add=True)
    checked=models.BooleanField(verbose_name='확인 여부',default=False)


