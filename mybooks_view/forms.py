from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


class LoginForm(forms.Form):
    username = forms.EmailField(help_text="Enter here email")
    password = forms.CharField(widget=forms.PasswordInput())
    message = None

    def clean_username(self):
        data = self.cleaned_data['username'].lower()

        if not data:
            raise ValidationError(_('Invalid email - string is empty'))
        return data

    def clean_password(self):
        data = self.cleaned_data['password']
        if not data:
            raise ValidationError(_('Invalid password - string is empty'))
        return data


class LogoutForm(forms.Form):
    message = forms.HiddenInput()

    def clean_username(self):
        data = self.cleaned_data['username'].lower()

        if not data:
            raise ValidationError(_('Invalid email - string is empty'))
        return data
