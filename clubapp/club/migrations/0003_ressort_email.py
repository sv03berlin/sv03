# Generated by Django 5.1.6 on 2025-03-16 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0002_alter_ressort_head'),
    ]

    operations = [
        migrations.AddField(
            model_name='ressort',
            name='email',
            field=models.CharField(default='', max_length=2048, verbose_name='Ressort Email'),
        ),
    ]
