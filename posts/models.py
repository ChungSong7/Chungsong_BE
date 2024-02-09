from django.db import models
from users.models import User
from boards.models import Board
import uuid


#게시글
class Post(models.Model):
    post_id = models.UUIDField(verbose_name='게시글ID', primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    board = models.ForeignKey(Board, verbose_name='게시판', on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(verbose_name='글제목',max_length=50)
    content = models.TextField(verbose_name='글내용')
    created_at = models.DateTimeField(verbose_name='작성시간',auto_now_add=True)
    author = models.ForeignKey(User, verbose_name='작성자', on_delete=models.SET_NULL,null=True, related_name ='posts')
    author_profile=models.IntegerField(verbose_name='글 프로필 이미지', default=0)
    cmter_size = models.IntegerField(verbose_name='댓작성자수',default =0)
    like_size = models.IntegerField(verbose_name='좋아요수',default=0)
    warn_size = models.IntegerField(verbose_name='신고수',default=0)
    anon_status = models.BooleanField(verbose_name='익명여부',default=True)
    display=models.BooleanField(verbose_name='삭제여부',default=False)

    def __str__(self):
        return str(f"({self.board.board_name}: {self.post_id})")
#이미지
class Image(models.Model):
    post = models.ForeignKey(Post,verbose_name='게시글', on_delete=models.CASCADE, related_name='images')
    imgfile = models.ImageField(verbose_name='이미지파일',null=True,upload_to="",blank=True)
    
    def __str__(self):
        return str(f"{self.post} \n {self.id}")