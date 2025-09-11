from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def lista_tareas(request):
    return render(request, 'tareas/lista.html')