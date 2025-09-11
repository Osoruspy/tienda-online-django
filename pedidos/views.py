from django.shortcuts import render

def lista_pedidos(request):
    return render(request, 'pedidos/lista.html')