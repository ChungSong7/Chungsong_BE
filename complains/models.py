from django.db import models
from posts.models import Post
from comments.models import Comment
from users.models import User
import uuid 


class Complain(models.Model):
    complain_id = models.UUIDField(verbose_name='신고ID', primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    comp_post = models.ForeignKey(Post, blank= True, null = True)
    comp_comment = models.ForeignKey(Comment, blank= True, null = True)
    comp_user = models.ForeignKey(User,verbose_name='신고자', on_delete=models.CASCADE)
    comped_user = models.ForeignKey(User,verbose_name='피신고자', on_delete=models.CASCADE, related_name='complains')
    comp_date = models.DateField('신고날짜',auto_now_add=True)

    CATEGOTY_CHOICES = ('불건전한 내용',
                '사기',
                '상업적 광고',
                '특정인에 대한 비난',
                '도배'
    )
    category = models.CharField(verbose_name='신고사유', max_length=20, choices=CATEGOTY_CHOICES)

    status = models.IntegerField(verbose_name='신고처리',default = 0)


