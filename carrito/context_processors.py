from .utils import obtener_carrito

def carrito_context(request):
    carrito = obtener_carrito(request)
    return {
        'carrito': carrito,
        'total_items_carrito': carrito.total_items if carrito else 0
    }