from django.db import models
from posts.models import Post,Comment
#from comments.models import Comment
from users.models import User
import uuid 
from django.utils import timezone


class Complain(models.Model):
    complain_id = models.UUIDField(verbose_name='신고ID', primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    comp_post = models.ForeignKey(Post, verbose_name='신고 게시글',blank= True, null = True,  on_delete=models.SET_NULL)
    comp_comment = models.ForeignKey(Comment, verbose_name='신고 댓글',blank= True, null = True,  on_delete=models.SET_NULL)
    comp_user = models.ForeignKey(User,verbose_name='신고자', on_delete=models.CASCADE)
    comped_user = models.ForeignKey(User,verbose_name='피신고자', on_delete=models.CASCADE, related_name='complains')
    created_at = models.DateTimeField(verbose_name='신고날짜',default=timezone.now)

    CATEGOTY_CHOICES = (
        ('불건전한 내용','불건전한 내용'),
        ('사기','사기'),
        ('상업적 광고','상업적 광고'),
        ('특정인에 대한 비난','특정인에 대한 비난'),
        ('도배','도배'),
        ('기타','기타')
    )
    category = models.CharField(verbose_name='신고사유', choices=CATEGOTY_CHOICES,max_length=50)
    status = models.CharField(verbose_name='신고처리상태',max_length=30, default='신고접수')


