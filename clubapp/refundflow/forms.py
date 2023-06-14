from django import forms

from . import models


class SubmitRefund(forms.Form):
    file = forms.FileField(required=True)
    reason = forms.CharField(required=True, max_length=255)
    amount = forms.DecimalField(required=True, max_digits=16, decimal_places=2)
    ressort = forms.CharField(required=True, max_length=255)
    annotation = forms.CharField(required=False, max_length=1023)


class AddTracking(forms.ModelForm[models.Tracking]):
    is_hour = forms.BooleanField(required=False)
    annotation = forms.CharField(required=False, max_length=1023)
    hour_count = forms.IntegerField(required=False)

    class Meta:
        model = models.Tracking
        fields = [
            "ressort",
            "date",
            "reason",
            "amount",
        ]
