from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class NewUserCreationForm(UserCreationForm):
    email = forms.EmailField(label=_("Email"), required=True)
    
    class Meta(UserCreationForm.Meta):
        fields = ("username", "email")
        
    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(_("A user with that email already exists."))
