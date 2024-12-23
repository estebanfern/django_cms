# Generated by Django 4.2 on 2024-10-15 02:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suscription', '0004_alter_suscription_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suscription',
            name='state',
            field=models.CharField(choices=[('active', 'Activo'), ('pending_payment', 'Pendiente de pago'), ('cancelled', 'Cancelado')], default='pending_payment', max_length=15, verbose_name='Tipo'),
        ),
    ]
