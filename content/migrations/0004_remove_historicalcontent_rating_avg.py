# Generated by Django 4.2 on 2024-09-30 06:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0003_content_rating_avg_historicalcontent_rating_avg'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalcontent',
            name='rating_avg',
        ),
    ]
