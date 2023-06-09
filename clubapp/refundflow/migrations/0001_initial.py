# Generated by Django 4.2 on 2023-06-13 11:32

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("club", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("reason", models.CharField(max_length=255)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=16)),
                ("approve_date", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("REC", "Eingegangen"), ("APP", "Genehmigt"), ("REJ", "Abgelehnt"), ("TRA", "Überwiesen")],
                        default="REC",
                        max_length=3,
                    ),
                ),
                ("annotation", models.CharField(max_length=1023)),
                ("invoice_path", models.FileField(upload_to="%Y/%m/")),
                (
                    "approved_by",
                    models.ForeignKey(
                        null=True, on_delete=django.db.models.deletion.PROTECT, related_name="user_approving", to=settings.AUTH_USER_MODEL
                    ),
                ),
                ("ressort", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="club.ressort")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, related_name="user_applying", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Tracking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date", models.DateField()),
                ("reason", models.CharField(max_length=255)),
                ("payment_type", models.CharField(default="hour", max_length=255)),
                ("hour_count", models.IntegerField(null=True)),
                ("hour_rate", models.DecimalField(decimal_places=2, max_digits=16, null=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=16)),
                ("annotation", models.CharField(default="", max_length=1023, null=True)),
                ("ressort", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="club.ressort")),
                ("transaction", models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to="refundflow.transaction")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
