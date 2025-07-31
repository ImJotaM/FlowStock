from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class SignUpForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        error_messages={
            'required': _("O campo de e-mail é obrigatório."),
            'invalid': _("Por favor, insira um endereço de e-mail válido."),
        }
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
        error_messages = {
            'password_mismatch': _("As senhas não conferem."),
            'username': {
                'unique': _("Este nome de usuário já está em uso. Por favor, escolha outro."),
                'required': _("O campo de nome de usuário é obrigatório."),
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Digite seu nome de usuário',
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Digite seu e-mail',
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Digite sua senha',
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirme sua senha',
        })

        for _, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control border-secondary'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError(_("Este endereço de e-mail já está cadastrado. Por favor, utilize outro."))
        return email

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Digite seu nome de usuário ou e-mail',
            'class': 'form-control border-secondary'
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Digite sua senha',
            'class': 'form-control border-secondary'
        })
        
        self.error_messages = {
            'invalid_login': _(
                "Por favor, insira um nome de usuário e senha corretos. Note que ambos "
                "os campos diferenciam maiúsculas e minúsculas."
            ),
            'inactive': _("Esta conta está inativa."),
        }

    def clean(self):
        username= self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password and '@' in username:
            try:
                user = User.objects.get(email=username.lower())
                
                self.cleaned_data['username'] = user.username

            except User.DoesNotExist:
                self.error_messages = {
                    'invalid_login': _(
                        "Por favor, insira um email e senha corretos. Note que a senha "
                        "diferencia maiúsculas e minúsculas."
                    ),
                }
                pass
        
        return super().clean()

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="",
        max_length=254,
        widget=forms.EmailInput(attrs={
            'autocomplete': 'email',
            'class': 'form-control border-secondary',
            'placeholder': 'Digite seu e-mail'
        })
    )

class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control border-secondary',
            'placeholder': 'Digite a nova senha'
        })
    )
    new_password2 = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control border-secondary',
            'placeholder': 'Confirme a nova senha'
        })
    )
