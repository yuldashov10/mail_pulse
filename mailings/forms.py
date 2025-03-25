from django import forms
from django.utils import timezone

from .models import Mailing


class MailingForm(forms.ModelForm):
    """Форма для создания и редактирования рассылки."""

    class Meta:
        model = Mailing
        fields = ("start_time", "end_time", "message", "recipients")
        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"},
            ),
        }

    def clean_start_time(self):
        start_time = self.cleaned_data["start_time"]
        if start_time < timezone.now():
            raise forms.ValidationError(
                "Дата и время первой отправки не могут быть в прошлом",
            )
        return start_time

    def clean(self) -> dict:
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError(
                "Дата окончания должна быть позже даты начала",
            )
        return cleaned_data
