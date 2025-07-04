# Generated by Django 4.2.1 on 2024-02-19 11:57

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_deleteduser_alter_user_email_alter_user_nickname_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailVarify',
            fields=[
                ('email_varify_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True, verbose_name='고유번호')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='이메일')),
                ('code', models.CharField(max_length=4, verbose_name='인증번호')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='인증코드 생성시간')),
            ],
        ),
    ]
