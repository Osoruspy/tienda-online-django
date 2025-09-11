from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Rol

class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'activo')
    list_filter = ('rol', 'activo', 'is_staff', 'is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('rol', 'telefono', 'direccion', 'fecha_nacimiento', 
                      'dni', 'fecha_contratacion', 'salario', 'activo')
        }),
    )

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Rol)