from django.db import models
from users.models import User
import uuid

#게시판
class Board(models.Model):
    board_id = models.IntegerField(verbose_name="게시판ID", primary_key=True, unique=True, editable=False)
    board_name = models.CharField(verbose_name="게시판이름", max_length = 10)

#게시글
class Post(models.Model):
    post_id = models.UUIDField(verbose_name='게시글ID', primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, verbose_name='게시판', related_name='posts')
    title = models.CharField(verbose_name='글제목',max_length=50)
    content = models.TextField(verbose_name='글내용')
    created_at = models.DateTimeField(verbose_name='작성시간',auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='작성자',related_name ='posts')
    cmter_size = models.IntegerField(verbose_name='댓작성자수',default =0)
    like_size = models.IntegerField(verbose_name='좋아요수',default=0)
    warn_size = models.IntegerField(verbose_name='신고수',default=0)
    anon_status = models.BooleanField(verbose_name='익명여부',default=True)

#이미지
class Image(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    imgfile = models.ImageField(verbose_name='이미지파일',null=True,upload_to="",blank=True)