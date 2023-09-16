# Generated by Django 4.2.3 on 2023-09-14 08:17

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reservationflow', '0002_alter_reservabelthing_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservationgroup',
            name='users',
            field=models.ManyToManyField(related_name='reservation_groups', to=settings.AUTH_USER_MODEL, verbose_name='Benutzer:innen in Reservierungsgruppe'),
        ),
        migrations.DeleteModel(
            name='ReservationGroupMembership',
        ),
    ]