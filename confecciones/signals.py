from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from pedidos.models import Pedido
from .models import Confeccion

@receiver(post_save, sender=Pedido)
def crear_confeccion_desde_pedido(sender, instance, created, **kwargs):
    """
    Crear automáticamente una confección cuando se crea un pedido de tipo confección
    """
    if created and instance.es_pedido_confeccion:
        # Calcular fecha de entrega por defecto (7 días hábiles)
        fecha_entrega = timezone.now() + timedelta(days=7)
        
        Confeccion.objects.create(
            pedido=instance,
            contacto=f"{instance.usuario.first_name} {instance.usuario.last_name}".strip() or instance.usuario.username,
            telefono_contacto=instance.telefono_contacto,
            email_contacto=instance.usuario.email,
            fecha_entrega=fecha_entrega,
            observaciones=instance.observaciones
        )

@receiver(post_save, sender=Confeccion)
def actualizar_estado_pedido(sender, instance, **kwargs):
    """
    Sincronizar el estado de la confección con el estado del pedido
    """
    if instance.pedido:
        # Mapear estados de confección a estados de pedido
        estado_map = {
            'pendiente': 'pendiente',
            'diseno': 'en_proceso',
            'corte': 'en_proceso',
            'confeccion': 'en_proceso',
            'terminado': 'completado',
            'entregado': 'completado',
            'cancelado': 'cancelado'
        }
        
        nuevo_estado = estado_map.get(instance.estado, 'pendiente')
        if instance.pedido.estado != nuevo_estado:
            instance.pedido.estado = nuevo_estado
            instance.pedido.save()