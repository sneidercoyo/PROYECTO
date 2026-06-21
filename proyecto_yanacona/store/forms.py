from django import forms
from django.core.validators import EmailValidator, RegexValidator
from django.core.exceptions import ValidationError
from .models import User, Contact


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Correo electrónico',
        max_length=150,
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-control-exact',
            'placeholder': 'tu@email.com'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        min_length=3,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control-exact',
            'placeholder': 'Tu contraseña'
        })
    )


class RegistroForm(forms.Form):
    name = forms.CharField(
        label='Nombre completo',
        min_length=3,
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$',
            message='Solo letras y espacios permitidos'
        )],
        widget=forms.TextInput(attrs={
            'class': 'form-control-exact',
            'placeholder': 'Tu nombre completo'
        })
    )
    email = forms.EmailField(
        label='Correo electrónico',
        max_length=150,
        validators=[EmailValidator()],
        widget=forms.EmailInput(attrs={
            'class': 'form-control-exact',
            'placeholder': 'tu@email.com'
        })
    )
    password = forms.CharField(
        label='Contraseña',
        min_length=3,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control-exact',
            'placeholder': 'Mínimo 3 caracteres'
        })
    )
    password_confirm = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control-exact',
            'placeholder': 'Repite tu contraseña'
        })
    )
    phone = forms.CharField(
        label='Teléfono',
        required=False,
        max_length=20,
        validators=[RegexValidator(
            regex=r'^[0-9\+\-\s]+$',
            message='Solo números, +, - y espacios'
        )],
        widget=forms.TextInput(attrs={
            'class': 'form-control-exact',
            'placeholder': '+57 310 123 4567'
        })
    )
    address = forms.CharField(
        label='Dirección',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control-exact',
            'rows': 2,
            'placeholder': 'Tu dirección de envío'
        })
    )
    city = forms.CharField(
        label='Ciudad',
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control-exact',
            'placeholder': 'Puerto Caicedo'
        })
    )

    def clean_email(self):
        email = self.cleaned_data['email'].lower().strip()
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo ya está registrado.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise ValidationError('Las contraseñas no coinciden.')
        return cleaned_data


class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control-exact',
                'placeholder': 'Tu nombre'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control-exact',
                'placeholder': 'tu@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control-exact',
                'placeholder': '+57 310 123 4567'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control-exact',
                'rows': 5,
                'placeholder': 'Escribe tu mensaje...'
            }),
        }

    def clean_email(self):
        return self.cleaned_data['email'].lower().strip()


class CheckoutForm(forms.Form):
    shipping_name = forms.CharField(
        label='Nombre completo',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control-exact',
            'placeholder': 'Nombre para el envío'
        })
    )
    shipping_address = forms.CharField(
        label='Dirección',
        widget=forms.Textarea(attrs={
            'class': 'form-control-exact',
            'rows': 2,
            'placeholder': 'Dirección de entrega'
        })
    )
    shipping_city = forms.CharField(
        label='Ciudad',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control-exact',
            'placeholder': 'Ciudad de entrega'
        })
    )
    shipping_phone = forms.CharField(
        label='Teléfono',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control-exact',
            'placeholder': 'Teléfono de contacto'
        })
    )
    notes = forms.CharField(
        label='Notas adicionales',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control-exact',
            'rows': 2,
            'placeholder': 'Instrucciones especiales...'
        })
    )
