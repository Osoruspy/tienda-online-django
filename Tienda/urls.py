from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/productos/', permanent=False), name='home'),
    path('admin/', admin.site.urls),
    
    # URLs con namespace correcto (solo las que están configuradas)
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),
    path('productos/', include('productos.urls', namespace='productos')),
    
    # Comentar temporalmente las apps que no están completamente configuradas
    # path('pedidos/', include('pedidos.urls', namespace='pedidos')),
    path('carrito/', include('carrito.urls', namespace='carrito')),
    # path('categorias/', include('categorias.urls', namespace='categorias')),
    # path('tareas/', include('tareas.urls', namespace='tareas')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)