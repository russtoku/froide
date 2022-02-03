# Generated by Django 2.1.4 on 2019-01-29 14:36

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("foirequest", "0033_requestdraft_flags"),
    ]

    operations = [
        migrations.AddField(
            model_name="foiattachment",
            name="timestamp",
            field=models.DateTimeField(default=django.utils.timezone.now, null=True),
        ),
        migrations.AlterField(
            model_name="foimessage",
            name="is_response",
            field=models.BooleanField(default=True, verbose_name="response?"),
        ),
    ]
