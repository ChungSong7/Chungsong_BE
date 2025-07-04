# Generated by Django 4.2.1 on 2024-02-06 13:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RoomRequest',
            fields=[
                ('room_request_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='고유번호')),
                ('pre_room', models.PositiveSmallIntegerField(verbose_name='변경전 호실')),
                ('new_room', models.PositiveSmallIntegerField(verbose_name='변경후 호실')),
                ('request_date', models.DateField(auto_now_add=True)),
                ('status', models.CharField(choices=[(0, '신청완료'), (1, '처리완료')], default=0, max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='신청자')),
            ],
        ),
    ]
