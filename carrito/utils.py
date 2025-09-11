from .models import Carrito
import uuid

def obtener_carrito(request):
    carrito = None
    
    # Para usuarios autenticados
    if request.user.is_authenticated:
        carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    
    # Para usuarios anónimos (usamos sesión)
    else:
        session_id = request.session.get('session_id')
        if session_id:
            try:
                carrito = Carrito.objects.get(sesion_id=session_id, usuario__isnull=True)
            except Carrito.DoesNotExist:
                carrito = None
        
        if not carrito:
            session_id = str(uuid.uuid4())
            request.session['session_id'] = session_id
            carrito = Carrito.objects.create(sesion_id=session_id)
    
    return carrito

def transferir_carrito_anonimo_a_usuario(request, usuario):
    """Transferir carrito de sesión a usuario cuando se registra/login"""
    session_id = request.session.get('session_id')
    if session_id:
        try:
            carrito_anonimo = Carrito.objects.get(sesion_id=session_id, usuario__isnull=True)
            
            # Verificar si el usuario ya tiene un carrito
            try:
                carrito_usuario = Carrito.objects.get(usuario=usuario)
                # Fusionar carritos
                for item in carrito_anonimo.items.all():
                    item_existente = carrito_usuario.items.filter(producto=item.producto).first()
                    if item_existente:
                        item_existente.cantidad += item.cantidad
                        item_existente.save()
                    else:
                        item.carrito = carrito_usuario
                        item.save()
                carrito_anonimo.delete()
            except Carrito.DoesNotExist:
                carrito_anonimo.usuario = usuario
                carrito_anonimo.sesion_id = None
                carrito_anonimo.save()
                
        except Carrito.DoesNotExist:
            pass