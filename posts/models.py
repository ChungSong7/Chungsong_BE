from django.db import models
from users.models import User
from boards.models import Board
import uuid,os


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

    def image_upload_path(instance, filename):
    # 파일 이름을 유니크한 UUID로 설정하거나 원하는 방식으로 변경할 수 있습니다.
    # 여기서는 UUID와 확장자를 조합하여 파일 이름을 설정합니다.
        ext = filename.split('.')[-1]
        post=instance.post
        filename = f"{post.post_id}_{instance.id}.{ext}"
        return os.path.join(f'post_images/{post.board.board_name}/', filename)
    
    #image_id=models.UUIDField(verbose_name='이미지ID', primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    post = models.ForeignKey(Post,verbose_name='게시글', on_delete=models.CASCADE, related_name='images')
    imgfile = models.ImageField(verbose_name='이미지파일',null=True,blank=True,upload_to=image_upload_path) #이미지업로드 경로 더 설정하자.

    def __str__(self):
        return str(f"{self.post} \n {self.id}")
    
#게시글 좋아하는 사람
class PostLiker(models.Model):
    postliker_id=models.UUIDField(verbose_name='liker 고유번호', primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    post = models.ForeignKey(Post, verbose_name='게시글',on_delete=models.CASCADE, related_name='likers')
    user = models.ForeignKey(User, verbose_name='좋아요 누른 유저', on_delete=models.SET_NULL,null=True, related_name ='like_posts')
    
    
#댓글
class Comment(models.Model):
    comment_id=models.UUIDField(verbose_name='댓글ID', primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    post=models.ForeignKey(Post, verbose_name='게시글',on_delete=models.CASCADE,related_name='comments')
    content = models.TextField(verbose_name='내용')
    created_at = models.DateTimeField(verbose_name='작성시간',auto_now_add=True)
    writer=models.ForeignKey(User,verbose_name='댓쓴이',on_delete=models.SET_NULL,null=True,related_name='comments')
    commenter = models.CharField(verbose_name='댓쓴이 표시 이름',max_length=20) #user.nickname 일때 ,사라진 user에 대해선 (탈퇴회원 구현 필요)
    like_size = models.IntegerField(verbose_name='좋아요수',default=0)
    warn_size = models.IntegerField(verbose_name='신고수',default=0)
    anon_status = models.BooleanField(verbose_name='익명여부',default=True)
    display=models.BooleanField(verbose_name='사용자화면',default=True)
    up_comment_id=models.UUIDField(verbose_name='어미 댓글',blank=True,null=True,default=None)

#게시글 좋아하는 사람
class CommentLiker(models.Model):
    commentliker_id=models.UUIDField(verbose_name='liker 고유번호', primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    comment = models.ForeignKey(Comment, verbose_name='댓글',on_delete=models.CASCADE, related_name='likers')
    user = models.ForeignKey(User, verbose_name='좋아요 누른 유저', on_delete=models.SET_NULL,null=True, related_name ='like_comments')
    

#댓쓴이 (for 익명번호 부여)
class Commenter(models.Model):
    commenter_id=models.UUIDField(verbose_name='댓쓴이ID', primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    post = models.ForeignKey(Post, verbose_name='게시글',on_delete=models.CASCADE, related_name='commenters')
    user = models.ForeignKey(User, verbose_name='댓쓴이', on_delete=models.SET_NULL,null=True, related_name ='commented_posts')
    anon_num = models.IntegerField(verbose_name='익명 번호')  #0이면 별명, 1이상이면 익명
