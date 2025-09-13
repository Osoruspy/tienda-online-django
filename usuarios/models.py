from django.contrib.auth.models import AbstractUser
from django.db import models

class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.nombre

class Usuario(AbstractUser):
    ROLES = (
        ('administrador', 'Administrador'),
        ('empleado', 'Empleado'),
        ('cliente', 'Cliente'),
    )
    
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    telefono = models.CharField(max_length=15, blank=True)
    direccion = models.TextField(blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)
    
    # Campos adicionales para clientes
    dni = models.CharField(max_length=20, blank=True, unique=True, null=True)
    
    # Campos adicionales para empleados
    fecha_contratacion = models.DateField(null=True, blank=True)
    salario = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.username} - {self.get_rol_display()}"
    
    def es_administrador(self):
        return self.rol == 'administrador' or self.is_superuser
    
    def es_empleado(self):
        return self.rol == 'empleado'
    
    def es_cliente(self):
        return self.rol == 'cliente'
    
        # Permisos específicos
    @property
    def puede_gestionar_pedidos(self):
        return self.es_administrador or self.has_perm('pedidos.can_manage_orders')

    @property
    def puede_editar_pedidos(self):
        return self.es_administrador or self.has_perm('pedidos.can_edit_orders')
    
    @property
    def puede_cancelar_pedidos(self):
        return self.es_administrador or self.has_perm('pedidos.can_cancel_orders')

    @property
    def puede_ver_todos_pedidos(self):
        return self.es_administrador or self.es_empleado
    
    @property
    def puede_gestionar_usuarios(self):
        return self.es_administrador
    
    @property
    def puede_gestionar_productos(self):
        return self.es_administrador or self.has_perm('productos.can_manage_products')

    class Meta:
        permissions = [
            ('gestionar_pedidos', 'Puede gestionar pedidos'),
            ('editar_pedidos', 'Puede editar pedidos'),
            ('cancelar_pedidos', 'Puede cancelar pedidos'),
            ('ver_todos_pedidos', 'Puede ver todos los pedidos'),
        ]