# Generated by Django 4.2.1 on 2024-02-22 17:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('complains', '0007_alter_complain_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='complain',
            old_name='comp_date',
            new_name='created_at',
        ),
    ]
