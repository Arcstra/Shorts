from django import forms
from .models import Client, Short


class RegisterForm(forms.ModelForm):
    username = forms.CharField(max_length=255)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.widgets.PasswordInput())
    password_again = forms.CharField(widget=forms.widgets.PasswordInput())

    class Meta:
        model = Client
        fields = ("username", "email", "password", )


class OnlyEmailForm(forms.Form):
    email = forms.EmailField(max_length=255)
    

class CodeFromEmailForm(forms.Form):
    code = forms.CharField(max_length=6)
    

class NewPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.widgets.PasswordInput())
    password_again = forms.CharField(widget=forms.widgets.PasswordInput())

    def is_valid(self) -> bool:
        return super().is_valid() and self.cleaned_data["password"] == self.cleaned_data["password_again"]
    

class AddShortForm(forms.ModelForm):
    class Meta:
        model = Short
        fields = ("title", "image", )
