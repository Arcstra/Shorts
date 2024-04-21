from django import forms


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=255)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.widgets.PasswordInput())
    password_again = forms.CharField(widget=forms.widgets.PasswordInput())

    def is_valid(self) -> bool:
        return super().is_valid() and self.cleaned_data["password"] == self.cleaned_data["password_again"]


class CodeFromEmailForm(forms.Form):
    code = forms.CharField(max_length=6)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.widgets.PasswordInput())


class OnlyEmailForm(forms.Form):
    email = forms.EmailField(max_length=255)


class NewPasswordForm(forms.Form):
    password = forms.CharField(widget=forms.widgets.PasswordInput())
    password_again = forms.CharField(widget=forms.widgets.PasswordInput())

    def is_valid(self) -> bool:
        return super().is_valid() and self.cleaned_data["password"] == self.cleaned_data["password_again"]


class AddShortForm(forms.Form):
    title = forms.CharField(max_length=255)
    image = forms.ImageField()
