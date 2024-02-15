from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from user.models import User


class UserCreationForm(UserCreationForm):
    
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields


class UserUpdateForm(forms.ModelForm):
    new_password = forms.CharField(widget=forms.PasswordInput, required=False)  # New password field
    class Meta:
        model = User
        fields = ["username", "full_name","new_password"]


class UserSearchForm(forms.Form):
    username = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Search by name"}
        )
    )