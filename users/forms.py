from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm

from users.models import User


class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "first_name",
            "last_name",
            "phone_number",
            "country",
            "avatar",
        )


class RegistrationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = (
            "email",
            "username",
            "password1",
            "password2",
        )
