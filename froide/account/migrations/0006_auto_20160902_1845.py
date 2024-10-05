# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-02 16:45


import django.contrib.auth.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_user_is_blocked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.ASCIIUsernameValidator()], verbose_name='username'),
        ),
    ]
