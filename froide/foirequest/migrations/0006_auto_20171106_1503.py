# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-06 14:03
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("publicbody", "0005_auto_20171106_1503"),
        ("foirequest", "0005_auto_20160902_1845"),
    ]

    operations = [
        migrations.CreateModel(
            name="RequestDraft",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("create_date", models.DateTimeField(auto_now_add=True)),
                ("save_date", models.DateTimeField(auto_now=True)),
                (
                    "subject",
                    models.CharField(
                        blank=True, max_length=255, verbose_name="subject"
                    ),
                ),
                ("body", models.TextField(blank=True, verbose_name="body")),
                ("full_text", models.BooleanField(default=False)),
                ("public", models.BooleanField(default=True)),
                ("reference", models.CharField(blank=True, max_length=255)),
                ("publicbodies", models.ManyToManyField(to="publicbody.PublicBody")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="foimessage",
            name="status",
            field=models.CharField(
                blank=True,
                choices=[
                    ("awaiting_user_confirmation", "Awaiting user confirmation"),
                    ("publicbody_needed", "Public Body needed"),
                    (
                        "awaiting_publicbody_confirmation",
                        "Awaiting Public Body confirmation",
                    ),
                    ("awaiting_response", "Awaiting response"),
                    ("awaiting_classification", "Request awaits classification"),
                    ("asleep", "Request asleep"),
                    ("resolved", "Request resolved"),
                ],
                default=None,
                max_length=50,
                null=True,
                verbose_name="Status",
            ),
        ),
        migrations.AlterField(
            model_name="foirequest",
            name="resolution",
            field=models.CharField(
                blank=True,
                choices=[
                    ("successful", "Request Successful"),
                    ("partially_successful", "Request partially successful"),
                    ("not_held", "Information not held"),
                    ("refused", "Request refused"),
                    ("user_withdrew_costs", "Request was withdrawn due to costs"),
                    ("user_withdrew", "Request was withdrawn"),
                ],
                max_length=50,
                verbose_name="Resolution",
            ),
        ),
        migrations.AlterField(
            model_name="foirequest",
            name="status",
            field=models.CharField(
                choices=[
                    ("awaiting_user_confirmation", "Awaiting user confirmation"),
                    ("publicbody_needed", "Public Body needed"),
                    (
                        "awaiting_publicbody_confirmation",
                        "Awaiting Public Body confirmation",
                    ),
                    ("awaiting_response", "Awaiting response"),
                    ("awaiting_classification", "Request awaits classification"),
                    ("asleep", "Request asleep"),
                    ("resolved", "Request resolved"),
                ],
                max_length=50,
                verbose_name="Status",
            ),
        ),
        migrations.AlterField(
            model_name="publicbodysuggestion",
            name="reason",
            field=models.TextField(
                blank=True,
                default="",
                verbose_name="Reason this Public Body fits the request",
            ),
        ),
    ]
