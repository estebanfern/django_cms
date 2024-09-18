# Generated by Django 4.2 on 2024-09-18 07:17

import ckeditor_uploader.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
        ('category', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Título')),
                ('summary', models.TextField(max_length=255, verbose_name='Resumen')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('date_create', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')),
                ('date_expire', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de expiración')),
                ('date_published', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de publicación')),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Contenido')),
                ('state', models.CharField(choices=[('draft', 'Borrador'), ('revision', 'Revisión'), ('to_publish', 'A publicar'), ('publish', 'Publicado'), ('inactive', 'Inactivo')], default='draft', max_length=20, verbose_name='Estado')),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Autor')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='category.category', verbose_name='Categoría')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'Contenido',
                'verbose_name_plural': 'Contenidos',
                'db_table': 'content',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, verbose_name='Correo Electrónico')),
                ('name', models.CharField(max_length=255, verbose_name='Nombre')),
                ('reason', models.CharField(choices=[('spam', 'Spam'), ('inappropriate', 'Contenido inapropiado'), ('abuse', 'Abuso o acoso')], max_length=50, verbose_name='Motivo')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='content.content', verbose_name='Contenido')),
                ('reported_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Reportado por')),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalContent',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Título')),
                ('summary', models.TextField(max_length=255, verbose_name='Resumen')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
                ('date_create', models.DateTimeField(blank=True, editable=False, verbose_name='Fecha de creacion')),
                ('date_expire', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de expiración')),
                ('date_published', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de publicación')),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(verbose_name='Contenido')),
                ('state', models.CharField(choices=[('draft', 'Borrador'), ('revision', 'Revisión'), ('to_publish', 'A publicar'), ('publish', 'Publicado'), ('inactive', 'Inactivo')], default='draft', max_length=20, verbose_name='Estado')),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('autor', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Autor')),
                ('category', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='category.category', verbose_name='Categoría')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Contenido',
                'verbose_name_plural': 'historical Contenidos',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
