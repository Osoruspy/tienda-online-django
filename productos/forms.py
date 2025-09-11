from django import forms
from .models import Producto, Categoria

class ProductoBusquedaForm(forms.Form):
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Buscar productos...',
            'class': 'form-control'
        })
    )
    
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.filter(activa=True),
        required=False,
        empty_label="Todas las categorías",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    ordenar_por = forms.ChoiceField(
        choices=[
            ('nombre', 'Nombre A-Z'),
            ('-nombre', 'Nombre Z-A'),
            ('precio', 'Precio: Menor a Mayor'),
            ('-precio', 'Precio: Mayor a Menor'),
            ('-fecha_creacion', 'Más recientes'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'precio_oferta', 'categoria', 'sku', 'stock', 'estado', 'destacado']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
        }