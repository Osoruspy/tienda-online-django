from django import forms
from .models import Confeccion, DetalleConfeccion, ItemAdicional
from django.utils import timezone
from datetime import timedelta

class ConfeccionForm(forms.ModelForm):
    class Meta:
        model = Confeccion
        fields = ['fecha_entrega', 'contacto', 'telefono_contacto', 'email_contacto', 'prioridad', 'observaciones']
        widgets = {
            'fecha_entrega': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono_contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'email_contacto': forms.EmailInput(attrs={'class': 'form-control'}),
            'prioridad': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer fecha mínima de entrega (mañana)
        min_date = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M')
        self.fields['fecha_entrega'].widget.attrs['min'] = min_date

class DetalleConfeccionForm(forms.ModelForm):
    class Meta:
        model = DetalleConfeccion
        fields = ['tipo_prenda', 'genero', 'nombre_diseno', 'cantidad', 'talla', 'color_principal', 'colores_secundarios', 'precio_unitario', 'observaciones']
        widgets = {
            'tipo_prenda': forms.Select(attrs={'class': 'form-select'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'nombre_diseno': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'talla': forms.Select(attrs={'class': 'form-select'}),
            'color_principal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ROJO, AZUL, NEGRO'}),
            'colores_secundarios': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: BLANCO, AMARILLO'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class ItemAdicionalForm(forms.ModelForm):
    class Meta:
        model = ItemAdicional
        fields = ['descripcion', 'cantidad', 'precio_adicional', 'observaciones']
        widgets = {
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'precio_adicional': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EstadoConfeccionForm(forms.Form):
    estado = forms.ChoiceField(
        choices=Confeccion.ESTADOS_CONFECCION,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Cambiar Estado'
    )
    observaciones = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Observaciones del cambio de estado'}),
        label='Observaciones'
    )