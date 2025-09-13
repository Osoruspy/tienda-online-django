from decimal import Decimal
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from productos.models import Producto
from django.contrib.auth import get_user_model


class Pedido(models.Model):
    ESTADOS_PEDIDO = (
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    )
    
    TIPOS_PEDIDO = (
        ('normal', 'Pedido Normal'),
        ('confeccion', 'Pedido de Confección'),
    )
    
    METODOS_PAGO = (
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta de Crédito/Débito'),
    )
    
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    estado = models.CharField(max_length=20, choices=ESTADOS_PEDIDO, default='pendiente')
    tipo_pedido = models.CharField(max_length=20, choices=TIPOS_PEDIDO, default='normal')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)],verbose_name='Total del Pedido')

    direccion_entrega = models.TextField(verbose_name='Dirección de Entrega')
    telefono_contacto = models.CharField(max_length=20, verbose_name='Teléfono de Contacto')
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='efectivo')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')
    es_urgente = models.BooleanField(default=False, verbose_name='¿Es urgente?')
    
    nombre_completo = models.CharField(max_length=100, default='')
    email = models.EmailField(default='')
    telefono = models.CharField(max_length=20, default='')
    direccion = models.TextField(default='')
    ciudad = models.CharField(max_length=50, default='')
    codigo_postal = models.CharField(max_length=10, default='')
    
    # Nuevos campos para checkout
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    impuestos = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    costo_envio = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    costo_envio = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)], verbose_name='Costo de Envío',help_text='Costo de envío. Puede ser 0 si es gratuito.')
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    # Información de envío y facturación
    nombre_completo = models.CharField(max_length=100, default='')
    email = models.EmailField(default='')
    telefono = models.CharField(max_length=20, default='')
    direccion = models.TextField(default='')
    ciudad = models.CharField(max_length=50, default='')
    codigo_postal = models.CharField(max_length=10, default='')
    
    # Métodos de pago
    METODOS_PAGO = (
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia Bancaria'),
        ('tarjeta_credito', 'Tarjeta de Crédito'),
        ('tarjeta_debito', 'Tarjeta de Débito'),
        ('mercado_pago', 'Mercado Pago'),
    )
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='efectivo')
    
    # Estados de pago
    ESTADOS_PAGO = (
        ('pendiente', 'Pendiente de Pago'),
        ('procesando', 'Procesando Pago'),
        ('pagado', 'Pagado'),
        ('fallido', 'Pago Fallido'),
        ('reembolsado', 'Reembolsado'),
    )
    estado_pago = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='pendiente')
    
    # Timestamps
    fecha_pago = models.DateTimeField(null=True, blank=True)
    
    def calcular_totales(self, costo_envio=None):
        """Calcular automáticamente los totales"""
        self.subtotal = sum(item.subtotal for item in self.items.all())
        # Impuestos (21% IVA como ejemplo)
        self.impuestos = self.subtotal * Decimal('0.21')
        
        # Envío: si se proporciona un costo, usarlo. Si no, calcular automáticamente.
        if costo_envio is not None:
            self.costo_envio = costo_envio
        else:
            # Envío gratuito sobre $5000
            self.costo_envio = Decimal('0') if self.subtotal > Decimal('5000') else Decimal('500')
        
        # Total se calcula con la propiedad, no se guarda en la base de datos
        # porque es una propiedad (read-only)
        self.save()
                
    def total(self):
        return self.subtotal + self.impuestos + self.costo_envio - self.descuento
    
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_creacion']
        permissions = [
            ('can_manage_orders', 'Puede gestionar pedidos'),
        ]
    
    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.get_full_name() or self.usuario.username}"
    
    def save(self, *args, **kwargs):
        # Calcular total automáticamente antes de guardar
        if self.pk:
            self.total = sum(item.subtotal for item in self.items.all())
        super().save(*args, **kwargs)
    
    @property
    def es_pedido_confeccion(self):
        return self.tipo_pedido == 'confeccion'
    
    @property
    def cantidad_items(self):
        return sum(item.cantidad for item in self.items.all())
    
    @property
    def estado_display(self):
        return dict(self.ESTADOS_PEDIDO).get(self.estado, self.estado)
    
    def puede_ser_modificado_por(self, usuario):
        """Verificar permisos de modificación"""
        if usuario.es_administrador:
            return True
        elif usuario.es_empleado:
            return self.estado in ['pendiente', 'confirmado']
        elif usuario == self.usuario:
            return self.estado == 'pendiente'
        return False
    
    def puede_ser_eliminado_por(self, usuario):
        """Verificar permisos de eliminación"""
        return usuario.es_administrador and self.estado == 'pendiente'


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    descripcion_personalizada = models.CharField(max_length=200, blank=True, verbose_name='Descripción Personalizada del Producto')
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedido'
        ordering = ['fecha_agregado']
    
    def __str__(self):
        if self.producto:
            return f"{self.cantidad} x {self.producto.nombre}"
        return f"{self.cantidad} x {self.descripcion_personalizada}"
    
    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad
    
    def save(self, *args, **kwargs):
        # Si es un producto existente, usar su precio actual
        if self.producto and not self.precio_unitario:
            self.precio_unitario = self.producto.precio_actual()
        super().save(*args, **kwargs)
        # Actualizar el total del pedido
        self.pedido.save()

class SeguimientoPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='seguimientos')
    estado = models.CharField(max_length=20, choices=Pedido.ESTADOS_PEDIDO)
    observaciones = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = 'Seguimiento de Pedido'
        verbose_name_plural = 'Seguimientos de Pedidos'
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Seguimiento #{self.id} - {self.pedido} - {self.estado}"
    