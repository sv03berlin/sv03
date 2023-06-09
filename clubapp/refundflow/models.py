from django.db import models

from clubapp.club.models import Resort, User


class Transaction(models.Model):
    class StatusChoice(models.TextChoices):
        RECEIVED = ("REC", "Eingegangen")
        APPROVED = ("APP", "Genehmigt")
        REJECTED = ("REJ", "Abgelehnt")
        TRANSFERRED = ("TRA", "Überwiesen")

    user = models.ForeignKey(User, on_delete=models.PROTECT, null=False, related_name="user_applying")
    date = models.DateField()
    reason = models.CharField(max_length=255)
    resort = models.ForeignKey(Resort, on_delete=models.PROTECT, null=False)
    amount = models.DecimalField(decimal_places=2, max_digits=16)
    approved_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, related_name="user_approving")
    approve_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=3, choices=StatusChoice.choices, default=StatusChoice.RECEIVED)
    annotation = models.CharField(max_length=1023)
    invoice_path = models.FileField(upload_to="%Y/%m/")

    def __str__(self) -> str:
        return f"{self.user} - {self.reason} - {self.date}"


class Tracking(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    date = models.DateField()
    reason = models.CharField(max_length=255)
    payment_type = models.CharField(max_length=255, default="hour")
    hour_count = models.IntegerField(null=True)
    hour_rate = models.DecimalField(decimal_places=2, max_digits=16, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=16)
    transaction = models.ForeignKey(Transaction, on_delete=models.PROTECT, null=True)
    resort = models.ForeignKey(Resort, on_delete=models.PROTECT, null=False)
    annotation = models.CharField(max_length=1023, default="", null=True)

    def __str__(self) -> str:
        return f"{self.user} - {self.reason} - {self.date}"
