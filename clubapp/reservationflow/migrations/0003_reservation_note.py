# Generated by Django 5.1.6 on 2025-03-31 09:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reservationflow', '0002_alter_reservablething_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='note',
            field=models.TextField(default='', verbose_name='Bemerkung'),
        ),
    ]
