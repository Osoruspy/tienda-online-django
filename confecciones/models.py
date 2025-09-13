from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from pedidos.models import Pedido

class Confeccion(models.Model):
    ESTADOS_CONFECCION = (
        ('pendiente', 'Pendiente'),
        ('diseno', 'En Diseño'),
        ('corte', 'En Corte'),
        ('confeccion', 'En Confección'),
        ('terminado', 'Terminado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )
    
    PRIORIDADES = (
        ('normal', 'Normal'),
        ('urgente', 'Urgente'),
        ('prioritario', 'Prioritario'),
    )
    
    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='confeccion')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    fecha_entrega = models.DateTimeField(verbose_name='Fecha de Entrega Prometida')
    fecha_terminado = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Terminación')
    contacto = models.CharField(max_length=100, verbose_name='Persona de Contacto')
    telefono_contacto = models.CharField(max_length=20, verbose_name='Teléfono de Contacto')
    email_contacto = models.EmailField(
        verbose_name='Email de Contacto',
        null=True,  # Permitir nulo temporalmente
        blank=True
    )
    estado = models.CharField(max_length=20, choices=ESTADOS_CONFECCION, default='pendiente')
    prioridad = models.CharField(max_length=20, choices=PRIORIDADES, default='normal')
    asignado_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='confecciones_asignadas')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones Generales')
    costo_estimado = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    class Meta:
        verbose_name = 'Confección'
        verbose_name_plural = 'Confecciones'
        ordering = ['prioridad', 'fecha_entrega']
        permissions = [
            ('can_manage_confecciones', 'Puede gestionar confecciones'),
        ]
    
    def __str__(self):
        return f"Confección #{self.id} - Pedido #{self.pedido.id} - {self.contacto}"
    
    def save(self, *args, **kwargs):
        # Convertir textos a mayúsculas
        for field in ['contacto', 'telefono_contacto', 'observaciones']:
            value = getattr(self, field, '')
            if value and isinstance(value, str):
                setattr(self, field, value.upper())
        super().save(*args, **kwargs)
    
    @property
    def dias_restantes(self):
        from django.utils import timezone
        if self.fecha_entrega:
            delta = self.fecha_entrega - timezone.now()
            return delta.days
        return None
    
    @property
    def esta_atrasado(self):
        from django.utils import timezone
        if self.fecha_entrega and timezone.now() > self.fecha_entrega:
            return self.estado not in ['terminado', 'entregado', 'cancelado']
        return False

class DetalleConfeccion(models.Model):
    TIPOS_PRENDA = (
        ('CAMISETA', 'Camiseta'),
        ('SHORT', 'Short'),
        ('MEDIAS', 'Medias'),
        ('MUSCULOSA', 'Musculosa'),
        ('CANGURO', 'Canguro con pantalón'),
        ('PANTALON', 'Pantalón'),
        ('GORRA', 'Gorra'),
        ('BUZO', 'Buzo'),
        ('CHAQUETA', 'Chaqueta'),
        ('OTRO', 'Otro'),
    )
    
    GENEROS = (
        ('HOMBRE', 'Hombre'),
        ('MUJER', 'Mujer'),
        ('UNISEX', 'Unisex'),
        ('NIÑO', 'Niño'),
        ('NIÑA', 'Niña'),
    )
    
    TALLAS = (
        ('XS', 'XS (Extra Small)'),
        ('S', 'S (Small)'),
        ('M', 'M (Medium)'),
        ('L', 'L (Large)'),
        ('XL', 'XL (Extra Large)'),
        ('XXL', 'XXL (2X Large)'),
        ('XXXL', 'XXXL (3X Large)'),
        ('UNITALLA', 'Unitalla'),
    )
    
    confeccion = models.ForeignKey(Confeccion, on_delete=models.CASCADE, related_name='detalles')
    tipo_prenda = models.CharField(max_length=20, choices=TIPOS_PRENDA)
    genero = models.CharField(max_length=10, choices=GENEROS)
    nombre_diseno = models.CharField(max_length=100, verbose_name='Nombre del Diseño')
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    talla = models.CharField(max_length=10, choices=TALLAS)
    color_principal = models.CharField(max_length=50, verbose_name='Color Principal')
    colores_secundarios = models.CharField(max_length=200, blank=True, verbose_name='Colores Secundarios')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    observaciones = models.TextField(blank=True, verbose_name='Observaciones Específicas')
    
    class Meta:
        verbose_name = 'Detalle de Confección'
        verbose_name_plural = 'Detalles de Confección'
    
    def __str__(self):
        return f"{self.cantidad} x {self.get_tipo_prenda_display()} - {self.talla}"
    
    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad
    
    def save(self, *args, **kwargs):
        # Convertir textos a mayúsculas
        for field in ['nombre_diseno', 'color_principal', 'colores_secundarios', 'observaciones']:
            value = getattr(self, field, '')
            if value and isinstance(value, str):
                setattr(self, field, value.upper())
        super().save(*args, **kwargs)

class ItemAdicional(models.Model):
    detalle = models.ForeignKey(DetalleConfeccion, on_delete=models.CASCADE, related_name='items_adicionales')
    descripcion = models.CharField(max_length=100, verbose_name='Descripción del Item')
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    precio_adicional = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    observaciones = models.CharField(max_length=200, blank=True)
    
    class Meta:
        verbose_name = 'Item Adicional'
        verbose_name_plural = 'Items Adicionales'
    
    def __str__(self):
        return f"{self.descripcion} - +${self.precio_adicional}"
    
    @property
    def subtotal(self):
        return self.precio_adicional * self.cantidad
    
    def save(self, *args, **kwargs):
        if self.descripcion and isinstance(self.descripcion, str):
            self.descripcion = self.descripcion.upper()
        if self.observaciones and isinstance(self.observaciones, str):
            self.observaciones = self.observaciones.upper()
        super().save(*args, **kwargs)