# Generated by Django 3.2 on 2023-02-28 05:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]