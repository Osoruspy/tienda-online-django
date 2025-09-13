from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from usuarios.models import Usuario
from pedidos.models import Pedido

class Command(BaseCommand):
    help = 'Crea grupos de permisos por defecto'
    
    def handle(self, *args, **options):
        # Grupo Administradores
        admin_group, created = Group.objects.get_or_create(name='Administradores')
        admin_perms = Permission.objects.filter(codename__in=[
            'gestionar_pedidos', 'editar_pedidos', 'cancelar_pedidos', 'ver_todos_pedidos'
        ])
        admin_group.permissions.set(admin_perms)
        
        # Grupo Empleados
        empleado_group, created = Group.objects.get_or_create(name='Empleados')
        empleado_perms = Permission.objects.filter(codename__in=[
            'gestionar_pedidos', 'cancelar_pedidos', 'ver_todos_pedidos'
        ])
        empleado_group.permissions.set(empleado_perms)
        
        self.stdout.write(
            self.style.SUCCESS('Grupos de permisos creados exitosamente')