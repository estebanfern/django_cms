from django.db import migrations

def create_groups_and_permissions(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')

    # Crear grupo Suscriptor con permisos
    suscriptor_group, created = Group.objects.get_or_create(name='Suscriptor')
    if created:
        comment_post_perm = Permission.objects.get(
            codename='comment_post',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        react_to_post_perm = Permission.objects.get(
            codename='react_to_post',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        report_post_perm = Permission.objects.get(
            codename='report_post',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        suscriptor_group.permissions.add(comment_post_perm, react_to_post_perm, report_post_perm)

    # Crear grupo Autor con permisos
    author_group, created = Group.objects.get_or_create(name='Autor')
    if created:
        create_content_perm = Permission.objects.get(
            codename='create_content',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        comment_post_perm = Permission.objects.get(
            codename='comment_post',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        react_to_post_perm = Permission.objects.get(
            codename='react_to_post',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        report_post_perm = Permission.objects.get(
            codename='report_post',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        author_group.permissions.add(create_content_perm, comment_post_perm, react_to_post_perm, report_post_perm)

    # Crear grupo Editor con permisos
    editor_group, created = Group.objects.get_or_create(name='Editor')
    if created:
        edit_content_perm = Permission.objects.get(
            codename='edit_content',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        comment_post_perm = Permission.objects.get(
            codename='comment_post',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        react_to_post_perm = Permission.objects.get(
            codename='react_to_post',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        report_post_perm = Permission.objects.get(
            codename='report_post',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        editor_group.permissions.add(edit_content_perm, comment_post_perm, react_to_post_perm, report_post_perm)

    # Crear grupo Publicador con permisos
    publicador_group, created = Group.objects.get_or_create(name='Publicador')
    if created:
        publish_content_perm = Permission.objects.get(
            codename='publish_content',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        comment_post_perm = Permission.objects.get(
            codename='comment_post',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        react_to_post_perm = Permission.objects.get(
            codename='react_to_post',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        report_post_perm = Permission.objects.get(
            codename='report_post',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        publicador_group.permissions.add(publish_content_perm, comment_post_perm, react_to_post_perm, report_post_perm)

    # Crear grupo Admin con permisos
    admin_group, created = Group.objects.get_or_create(name='Admin')
    if created:
        create_users_perm = Permission.objects.get(
            codename='create_users',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        edit_users_perm = Permission.objects.get(
            codename='edit_users',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        delete_users_perm = Permission.objects.get(
            codename='delete_users',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        block_users_perm = Permission.objects.get(
            codename='block_users',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        unblock_users_perm = Permission.objects.get(
            codename='unblock_users',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        reset_passwords_perm = Permission.objects.get(
            codename='reset_passwords',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        view_users_perm = Permission.objects.get(
            codename='view_users',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        view_roles_perm = Permission.objects.get(
            codename='view_roles',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        create_roles_perm = Permission.objects.get(
            codename='create_roles',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        edit_roles_perm = Permission.objects.get(
            codename='edit_roles',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        delete_roles_perm = Permission.objects.get(
            codename='delete_roles',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        assign_roles_perm = Permission.objects.get(
            codename='assign_roles',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        remove_roles_perm = Permission.objects.get(
            codename='remove_roles',
            content_type__app_label='app',
            content_type__model='customuser'
        )
        admin_group.permissions.add(
            create_users_perm, edit_users_perm, delete_users_perm,
            block_users_perm, unblock_users_perm, reset_passwords_perm,
            view_users_perm, view_roles_perm, create_roles_perm,
            edit_roles_perm, delete_roles_perm, assign_roles_perm,
            remove_roles_perm
        )

class Migration(migrations.Migration):
    dependencies = [
        ('app', '0011_alter_customuser_options'),
    ]

    operations = [
        migrations.RunPython(create_groups_and_permissions),
    ]