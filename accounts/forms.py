from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class SignUpForm(UserCreationForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Digite seu nome de usuário',
            'class': 'form-control border-secondary'
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Digite seu e-mail',
            'class': 'form-control border-secondary'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Digite sua senha',
            'class': 'form-control border-secondary'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirme sua senha',
            'class': 'form-control border-secondary'
        })

    email = forms.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        
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