# Generated by Django 4.2 on 2024-10-25 22:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0010_content_important_historicalcontent_important'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalcontent',
            name='important',
        ),
    ]
