# Generated by Django 5.0.6 on 2024-06-13 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('club', '0008_user_member_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='internal_name',
            field=models.CharField(default='', max_length=63, unique=True, verbose_name='Mitgliedschaftsart'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ressort',
            name='internal_name',
            field=models.CharField(default='', max_length=63, unique=True, verbose_name='Mitgliedschaftsart'),
            preserve_default=False,
        ),
    ]
