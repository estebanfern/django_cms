# Generated by Django 5.1 on 2024-08-28 21:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_alter_customuser_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'permissions': [('create_content', 'Crear contenidos'), ('edit_content', 'Editar contenidos'), ('publish_content', 'Publicar contenidos'), ('manage_roles', 'Gestionar roles'), ('manage_users', 'Gestionar usuarios')]},
        ),
    ]
