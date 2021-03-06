# Generated by Django 2.2.7 on 2020-05-06 18:50

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('gamesrec', '0002_auto_20200506_1817'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usersession',
            old_name='timestamp',
            new_name='active_timestamp',
        ),
        migrations.AddField(
            model_name='usersession',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
