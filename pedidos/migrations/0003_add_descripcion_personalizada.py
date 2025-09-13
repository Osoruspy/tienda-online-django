from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('pedidos', '0002_remove_pedido_total_pedido_ciudad_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='itempedido',
            name='descripcion_personalizada',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Descripción Personalizada'),
        ),
    ]
    