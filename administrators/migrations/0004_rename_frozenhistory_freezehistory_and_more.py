# Generated by Django 4.2.1 on 2024-02-19 05:19

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('administrators', '0003_frozenhistory'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FrozenHistory',
            new_name='FreezeHistory',
        ),
        migrations.RenameField(
            model_name='freezehistory',
            old_name='frozen_history_id',
            new_name='freeze_history_id',
        ),
    ]
