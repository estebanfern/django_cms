# Generated by Django 4.2 on 2024-09-03 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='date_expire',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de expiración'),
        ),
    ]
