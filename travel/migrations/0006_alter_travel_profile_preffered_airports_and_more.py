# Generated by Django 5.0 on 2024-01-29 21:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("travel", "0005_rename_vacation_type_travel_profile_vacation_types"),
    ]

    operations = [
        migrations.AlterField(
            model_name="travel_profile",
            name="preffered_airports",
            field=models.ManyToManyField(
                related_name="preffered_by", to="travel.airport"
            ),
        ),
        migrations.CreateModel(
            name="Airport_suitability",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("suitability", models.IntegerField()),
                (
                    "airport",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="suitable_for",
                        to="travel.airport",
                    ),
                ),
                (
                    "vacation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="suitable",
                        to="travel.vacation_type",
                    ),
                ),
            ],
        ),
    ]
