from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroClienteForm

def registro_cliente(request):
    if request.method == 'POST':
        form = RegistroClienteForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido a nuestra tienda.')
            return redirect('productos:lista')
    else:
        form = RegistroClienteForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})

@login_required
def perfil_usuario(request):
    return render(request, 'usuarios/perfil.html', {'usuario': request.user})

def redireccion_despues_login(request):
    """Redirección personalizada después del login"""
    if request.user.is_authenticated:
        if request.user.es_administrador():
            return redirect('admin:index')
        elif request.user.es_empleado():
            return redirect('usuarios:panel_empleado')
        else:
            return redirect('productos:lista')
    return redirect('usuarios:login')

@login_required
def redireccion_despues_login(request):
    """Redirección inteligente después del login basada en el rol del usuario"""
    if request.user.es_administrador():
        return redirect('admin:index')
    elif request.user.es_empleado():
        return redirect('admin:index')  # O puedes crear un panel para empleados
    else:
        return redirect('productos:lista')