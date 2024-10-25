# Generated by Django 4.2 on 2024-10-22 03:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0002_category_stripe_price_id_category_stripe_product_id'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('suscription', '0006_alter_suscription_state'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='suscription',
            options={'verbose_name': 'Suscripción', 'verbose_name_plural': 'Suscripciones'},
        ),
        migrations.AlterField(
            model_name='suscription',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='category.category', verbose_name='Categoría'),
        ),
        migrations.AlterField(
            model_name='suscription',
            name='date_subscribed',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Suscripción'),
        ),
        migrations.AlterField(
            model_name='suscription',
            name='state',
            field=models.CharField(choices=[('active', 'Activo'), ('cancelled', 'Cancelado'), ('pending_cancellation', 'Pendiente de cancelación')], default='active', max_length=20, verbose_name='Estado de la Suscripción'),
        ),
        migrations.AlterField(
            model_name='suscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Usuario'),
        ),
    ]
