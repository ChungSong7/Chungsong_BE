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
    author = models.ForeignKey(User, verbose_name='글쓴이', on_delete=models.SET_NULL,null=True, related_name ='posts')
    author_profile=models.IntegerField(verbose_name='글 프로필 이미지', default=0)
    comment_size = models.IntegerField(verbose_name='댓글수',default =0)
    like_size = models.IntegerField(verbose_name='좋아요수',default=0)
    warn_size = models.IntegerField(verbose_name='신고수',default=0)
    anon_status = models.BooleanField(verbose_name='익명여부',default=True)
    display=models.BooleanField(verbose_name='사용자화면',default=True)

    def __str__(self):
        return str(f"({self.board.board_name}: {self.post_id})")
#이미지
class Image(models.Model):
    post = models.ForeignKey(Post,verbose_name='게시글', on_delete=models.CASCADE, related_name='images')
    imgfile = models.ImageField(verbose_name='이미지파일',null=True,upload_to="",blank=True) #이미지업로드 경로 더 설정하자.
    
    def __str__(self):
        return str(f"{self.post} \n {self.id}")
    
#댓글
class Comment(models.Model):
    comment_id=models.UUIDField(verbose_name='댓글ID', primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    post=models.ForeignKey(Post, verbose_name='게시글',on_delete=models.CASCADE,related_name='comments')
    content = models.TextField(verbose_name='내용')
    created_at = models.DateTimeField(verbose_name='작성시간',auto_now_add=True)
    commenter = models.CharField(verbose_name='댓쓴이',max_length=20) #user.nickname 일때 ,사라진 user에 대해선 (탈퇴회원 구현 필요)
    like_size = models.IntegerField(verbose_name='좋아요수',default=0)
    warn_size = models.IntegerField(verbose_name='신고수',default=0)
    anon_status = models.BooleanField(verbose_name='익명여부',default=True)
    display=models.BooleanField(verbose_name='사용자화면',default=True)

#댓쓴이 (for 익명번호 부여)
class Commenter(models.Model):
    commenter_id=models.UUIDField(verbose_name='댓쓴이ID', primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    post = models.ForeignKey(Post, verbose_name='게시글',on_delete=models.CASCADE, related_name='commenters')
    user = models.ForeignKey(User, verbose_name='댓쓴이', on_delete=models.SET_NULL,null=True, related_name ='comments')
    anon_num = models.IntegerField(verbose_name='익명 번호')  #0이면 별명, 1이상이면 익명
