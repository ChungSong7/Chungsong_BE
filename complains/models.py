from django.db import models
from posts.models import Post
from comments.models import Comment
from users.models import User
import uuid 


class Complain(models.Model):
    complain_id = models.UUIDField(verbose_name='신고ID', primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    comp_post = models.ForeignKey(Post, on_delete=models.SET_NULL, blank= True, null = True)
    comp_comment = models.ForeignKey(Comment, on_delete=models.SET_NULL,blank= True, null = True)
    comp_user = models.ForeignKey(User,verbose_name='신고자', on_delete=models.CASCADE)
    comped_user = models.ForeignKey(User,verbose_name='피신고자', on_delete=models.CASCADE, related_name='complains')
    comp_date = models.DateField('신고날짜',auto_now_add=True)

    CATEGORY_CHOICES = [
        ('불건전한 내용', '불건전한 내용'),
        ('사기', '사기'),
        ('상업적 광고', '상업적 광고'),
        ('특정인에 대한 비난', '특정인에 대한 비난'),
        ('도배', '도배'),
        ('기타', '기타')
    ]

    category = models.CharField(verbose_name='신고사유', max_length=20, choices=CATEGORY_CHOICES)

    STATUS_CHOICES = [
        (0,'요청중'),
        (1,'처리완료')
    ]
    status = models.IntegerField(verbose_name='신고처리상태', choices=STATUS_CHOICES, default = 0)


