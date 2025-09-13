from django.db import models
from django.core.validators import MinValueValidator
from confecciones.models import Confeccion

class Cuenta(models.Model):
    confeccion = models.ForeignKey(Confeccion, on_delete=models.CASCADE)
    deuda = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.BooleanField(default=True)
    fecha = models.DateTimeField(auto_now=True)
    obs = models.CharField(max_length=50, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            if isinstance(field, models.CharField):
                valor = getattr(self, field.name)
                if isinstance(valor, str):
                    setattr(self, field.name, valor.upper())
        super().save(*args, **kwargs)
    
    @property
    def saldo_pendiente(self):
        return self.deuda - self.monto_pagado
    
    def __str__(self):
        return f"Cuenta - {self.confeccion}"

class DetallePago(models.Model):
    cuenta = models.ForeignKey(Cuenta, on_delete=models.CASCADE, related_name='detalles_pago')
    monto = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=20, choices=(
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('TARJETA', 'Tarjeta'),
        ('OTRO', 'Otro'),
    ), default='EFECTIVO')
    estado = models.BooleanField(default=True)
    obs = models.CharField(max_length=50, null=True, blank=True)
    
    def save(self, *args, **kwargs):
        # Actualizar monto pagado en la cuenta principal
        if self.pk is None:  # Solo si es nuevo pago
            self.cuenta.monto_pagado += self.monto
            self.cuenta.save()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Pago ${self.monto} - {self.cuenta}"