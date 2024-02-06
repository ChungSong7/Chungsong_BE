from django.db import models
from users.models import User

class ChangeRoomRequest(models.Model):
    STATUS_CHOICES = ((0,'신청완료'),(1,'처리완료'))

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pre_room = models.PositiveSmallIntegerField(verbose_name='변경전 호실')
    new_room = models.PositiveSmallIntegerField(verbose_name='변경후 호실')
    request_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=0)