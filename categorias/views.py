from django.shortcuts import render

def lista_categorias(request):
    return render(request, 'categorias/lista.html')