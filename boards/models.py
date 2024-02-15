from django.db import models


#게시판
class Board(models.Model):
    board_id = models.AutoField(verbose_name="게시판ID", primary_key=True, unique=True, editable=False)
    board_name = models.CharField(verbose_name="게시판이름", max_length = 10)
    
    def __str__(self):
        return self.board_name