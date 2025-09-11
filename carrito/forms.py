from django import forms
from .models import ItemCarrito

class AgregarAlCarritoForm(forms.Form):
    cantidad = forms.IntegerField(
        min_value=1,
        max_value=100,
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'style': 'width: 80px;'
        })
    )

class ActualizarCantidadForm(forms.ModelForm):
    class Meta:
        model = ItemCarrito
        fields = ['cantidad']
        widgets = {
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'max': '100',
                'style': 'width: 80px;'
            })
        }