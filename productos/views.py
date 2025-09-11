from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Producto, Categoria
from .forms import ProductoBusquedaForm

def lista_productos(request):
    form = ProductoBusquedaForm(request.GET or None)
    productos = Producto.objects.filter(estado='activo')
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        categoria = form.cleaned_data.get('categoria')
        ordenar_por = form.cleaned_data.get('ordenar_por') or '-fecha_creacion'
        
        if query:
            productos = productos.filter(
                Q(nombre__icontains=query) |
                Q(descripcion__icontains=query) |
                Q(categoria__nombre__icontains=query)
            )
        
        if categoria:
            productos = productos.filter(categoria=categoria)
        
        productos = productos.order_by(ordenar_por)
    else:
        productos = productos.order_by('-fecha_creacion')
    
    categorias = Categoria.objects.filter(activa=True)
    
    context = {
        'productos': productos,
        'form': form,
        'categorias': categorias,
    }
    return render(request, 'productos/lista.html', context)

def detalle_producto(request, slug):
    producto = get_object_or_404(Producto, slug=slug, estado='activo')
    productos_relacionados = Producto.objects.filter(
        categoria=producto.categoria,
        estado='activo'
    ).exclude(id=producto.id)[:4]
    
    context = {
        'producto': producto,
        'productos_relacionados': productos_relacionados,
    }
    return render(request, 'productos/detalle.html', context)

def por_categoria(request, slug_categoria):
    categoria = get_object_or_404(Categoria, slug=slug_categoria, activa=True)
    productos = Producto.objects.filter(categoria=categoria, estado='activo')
    
    form = ProductoBusquedaForm(request.GET or None)
    if form.is_valid():
        query = form.cleaned_data.get('query')
        ordenar_por = form.cleaned_data.get('ordenar_por') or '-fecha_creacion'
        
        if query:
            productos = productos.filter(
                Q(nombre__icontains=query) |
                Q(descripcion__icontains=query)
            )
        
        productos = productos.order_by(ordenar_por)
    else:
        productos = productos.order_by('-fecha_creacion')
    
    context = {
        'categoria': categoria,
        'productos': productos,
        'form': form,
    }
    return render(request, 'productos/por_categoria.html', context)