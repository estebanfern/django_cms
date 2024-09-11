# Generated by Django 4.2 on 2024-09-06 23:47

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
        migrations.AlterField(
            model_name='content',
            name='date_published',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de publicación'),
        ),
        migrations.AlterField(
            model_name='historicalcontent',
            name='date_expire',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de expiración'),
        ),
        migrations.AlterField(
            model_name='historicalcontent',
            name='date_published',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Fecha de publicación'),
        ),
    ]