# Generated by Django 5.0.6 on 2024-06-13 06:52

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=63, unique=True, verbose_name='Mitgliedschaftsart')),
                ('internal_name', models.CharField(max_length=63, unique=True, verbose_name='Interner Name')),
                ('work_hours', models.IntegerField(verbose_name='Arbeitsstunden')),
                ('work_hours_boat_owner', models.IntegerField(verbose_name='Arbeitsstunden Bootseigner:in')),
                ('work_hours_club_boat_user', models.IntegerField(verbose_name='Arbeitsstunden Clubbootnutzer:in')),
                ('work_compensation', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Entschädigung pro Stunde in €')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('license', models.CharField(blank=True, max_length=63, verbose_name='Lizenznummer')),
                ('can_create_invoices', models.BooleanField(default=False, verbose_name='Nutzer darf Rechnungen erstellen')),
                ('is_boat_owner', models.BooleanField(default=False, verbose_name='Nutzer ist Bootseigner:in')),
                ('is_clubboat_user', models.BooleanField(default=False, verbose_name='Nutzer ist Clubbootnutzer:in')),
                ('birthday', models.DateField(default=None, null=True, verbose_name='Geburtstag')),
                ('openid_sub', models.UUIDField(blank=True, null=True, verbose_name='OpenID Sub')),
                ('member_id', models.CharField(blank=True, default='', max_length=32, verbose_name='Mitgliedsnummer')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Ressort',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=63, unique=True, verbose_name='Ressortname')),
                ('internal_name', models.CharField(max_length=63, unique=True, verbose_name='Interner Ressortname')),
                ('is_accounting_ressort', models.BooleanField(default=False, verbose_name='Buchhaltungsressort')),
                ('head', models.ManyToManyField(related_name='ressort_head', to=settings.AUTH_USER_MODEL, verbose_name='Leiter:in')),
            ],
        ),
        migrations.CreateModel(
            name='MembershipYear',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(verbose_name='Jahr')),
                ('work_hours', models.IntegerField(default=0, verbose_name='Arbeitsstunden (Überschreiben für ausgewähltes Jahr)')),
                ('work_hours_boat_owner', models.IntegerField(default=0, verbose_name='Arbeitsstunden Bootseigner:in (Überschreiben für ausgewähltes Jahr)')),
                ('work_hours_club_boat_user', models.IntegerField(default=0, verbose_name='Arbeitsstunden Clubbootnutzer:in (Überschreiben für ausgewähltes Jahr)')),
                ('work_compensation', models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='Entschädigung pro Stunde in € (Überschreiben für ausgewähltes Jahr)')),
                ('full_work_compensation', models.BooleanField(default=False, verbose_name='Vollständige Entschädigung erfolgt')),
                ('membership_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='club.membership', verbose_name='Mitgliedschaftsart')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membership_years', to=settings.AUTH_USER_MODEL, verbose_name='Nutzer')),
            ],
            options={
                'verbose_name': 'Membership in year',
                'verbose_name_plural': 'Memberships in years',
                'unique_together': {('user', 'year')},
            },
        ),
    ]
