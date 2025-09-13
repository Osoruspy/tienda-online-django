from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Redirigir la raíz a productos
    path('', RedirectView.as_view(url='/productos/', permanent=False), name='home'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Incluir las URLs de las apps
    path('productos/', include('productos.urls', namespace='productos')),
    path('usuarios/', include('usuarios.urls', namespace='usuarios')),
    path('carrito/', include('carrito.urls', namespace='carrito')),
    path('pedidos/', include('pedidos.urls', namespace='pedidos')),
    path('confecciones/', include('confecciones.urls', namespace='confecciones')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
