# Generated by Django 5.1 on 2024-08-29 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_alter_customuser_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='about',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]