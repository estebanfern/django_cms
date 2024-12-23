# Generated by Django 4.2 on 2024-11-05 04:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_customuser_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'permissions': [('create_content', 'Crear contenidos'), ('edit_content', 'Editar contenidos'), ('publish_content', 'Publicar contenidos'), ('comment_post', 'Comentar contenidos'), ('react_to_post', 'Reaccionar a contenidos'), ('report_post', 'Reportar contenidos'), ('view_content', 'Ver contenidos'), ('edit_is_active', 'Editar estado de contenidos'), ('block_content', 'Bloquear contenidos'), ('set_important_content', 'Editar contenido destacado'), ('create_roles', 'Crear roles'), ('edit_roles', 'Editar roles'), ('delete_roles', 'Eliminar roles'), ('assign_roles', 'Asignar roles a usuarios'), ('remove_roles', 'Quitar roles a usuarios'), ('view_roles', 'Ver roles'), ('create_users', 'Crear usuarios'), ('edit_users', 'Editar usuarios'), ('delete_users', 'Eliminar usuarios'), ('block_users', 'Bloquear usuarios'), ('unblock_users', 'Desbloquear usuarios'), ('reset_passwords', 'Restablecer contraseñas'), ('view_users', 'Ver usuarios'), ('create_category', 'Crear categorías'), ('view_category', 'Ver categorías'), ('edit_category', 'Editar categorías'), ('delete_category', 'Eliminar categorías'), ('activate_category', 'Activar categorías'), ('deactivate_category', 'Desactivar categorías'), ('view_reports', 'Ver reportes'), ('view_stadistics', 'Ver estadisticas'), ('view_finances', 'Ver finanzas')], 'verbose_name': 'Usuario', 'verbose_name_plural': 'Usuarios'},
        ),
    ]
