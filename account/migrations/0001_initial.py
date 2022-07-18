# Generated by Django 4.0.4 on 2022-04-17 19:10

import account.models
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('point', models.PositiveIntegerField(default=0)),
                ('nickname', models.CharField(default='', max_length=10, unique=True, verbose_name='닉네임')),
                ('full_name', models.CharField(blank=True, max_length=10, verbose_name='이름')),
                ('phone_number', models.CharField(blank=True, max_length=255)),
                ('birth_year', models.IntegerField(null=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_verify', models.BooleanField(default=False)),
                ('joined_at', models.DateTimeField(default=datetime.datetime.now)),
                ('avater', models.ImageField(default='avater.jpg', upload_to=account.models.upload_to)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AuthMobile',
            fields=[
                ('phone_number', models.CharField(max_length=15, primary_key=True, serialize=False)),
                ('auth_number', models.IntegerField()),
            ],
            options={
                'db_table': 'auth_mobile',
            },
        ),
        migrations.CreateModel(
            name='UserWithdraw',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.BigIntegerField()),
                ('bank_account', models.CharField(max_length=255)),
                ('is_done', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'account_user_withdraw',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='UserShippingAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_name', models.CharField(max_length=255)),
                ('receiver', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=255)),
                ('base_address', models.CharField(max_length=255)),
                ('detail_address', models.CharField(max_length=255)),
                ('zipcode', models.IntegerField()),
                ('is_default', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'account_user_shipping_address',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='UserPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.BigIntegerField()),
                ('place', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'account_user_point',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='UserMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('next_url', models.CharField(max_length=255, null=True)),
                ('created_at', models.DateTimeField(default=datetime.datetime.now)),
                ('is_read', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'account_user_message',
                'managed': True,
            },
        ),
    ]
