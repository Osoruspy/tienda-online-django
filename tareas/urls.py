from django.urls import path
from . import views

app_name = 'tareas'  # ← Esta línea es crucial

urlpatterns = [
    path('', views.lista_tareas, name='lista'),
]