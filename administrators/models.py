from django.db import models
from users.models import User
import uuid

class RoomRequest(models.Model):
    STATUS_CHOICES = ((0,'신청완료'),(1,'처리완료'))

    room_request_id=models.UUIDField(verbose_name='고유번호',primary_key=True, default=uuid.uuid4, unique=True,editable=False)
    user = models.ForeignKey(User, verbose_name='신청자',on_delete=models.CASCADE)
    pre_room = models.PositiveSmallIntegerField(verbose_name='변경전 호실')
    new_room = models.PositiveSmallIntegerField(verbose_name='변경후 호실')
    request_date = models.DateTimeField(verbose_name='신청날짜',auto_now_add=True)
    status = models.IntegerField(verbose_name='처리상태',choices=STATUS_CHOICES, default=0)

    def __str__(self):
        return str(f'{self.user.username} : {self.pre_room} -> {self.new_room}    {self.status}')