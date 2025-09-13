from django import forms
from .models import Pedido, ItemPedido
from productos.models import Producto

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['nombre_completo', 'email', 'telefono', 'direccion', 'ciudad', 'codigo_postal', 'metodo_pago', 'observaciones']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@email.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+54 11 1234-5678'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-select'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Observaciones adicionales'}),
        }
        labels = {
            'nombre_completo': 'Nombre Completo',
            'email': 'Email',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
            'codigo_postal': 'Código Postal',
            'metodo_pago': 'Método de Pago',
            'observaciones': 'Observaciones',
        }

class ItemPedidoForm(forms.ModelForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(estado='activo'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = ItemPedido
        fields = ['producto', 'cantidad', 'descripcion_personalizada', 'precio_unitario']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'descripcion_personalizada': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descripción del producto personalizado'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        descripcion_personalizada = cleaned_data.get('descripcion_personalizada')
        
        if not producto and not descripcion_personalizada:
            raise forms.ValidationError("Debe seleccionar un producto o ingresar una descripción personalizada.")
        
        return cleaned_data

# Formularios de Checkout (actualizados)
class DireccionEnvioForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['nombre_completo', 'email', 'telefono', 'direccion', 'ciudad', 'codigo_postal']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@email.com'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+54 11 1234-5678'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dirección completa'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad'}),
            'codigo_postal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código Postal'}),
        }
        labels = {
            'nombre_completo': 'Nombre Completo',
            'email': 'Email',
            'telefono': 'Teléfono',
            'direccion': 'Dirección de Envío',
            'ciudad': 'Ciudad',
            'codigo_postal': 'Código Postal',
        }

class MetodoPagoForm(forms.Form):
    metodo_pago = forms.ChoiceField(
        choices=Pedido.METODOS_PAGO,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Método de Pago',
        initial='efectivo'
    )
    
    aceptar_terminos = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Acepto los términos y condiciones'
    )

class ConfirmacionPagoForm(forms.Form):
    numero_tarjeta = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234 5678 9012 3456', 'maxlength': '19'}),
        label='Número de Tarjeta'
    )
    fecha_vencimiento = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/AA', 'maxlength': '5'}),
        label='Fecha de Vencimiento'
    )
    codigo_seguridad = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '123', 'maxlength': '3'}),
        label='CVV'
    )
    nombre_titular = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Como aparece en la tarjeta'}),
        label='Nombre del Titular'
    )