from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class RegistroClienteForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label='Nombre')
    last_name = forms.CharField(required=True, label='Apellido')
    
    class Meta:
        model = Usuario
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'telefono', 'direccion', 'fecha_nacimiento', 'dni',
                 'password1', 'password2')
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.rol = 'cliente'
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user