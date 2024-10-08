# Generated by Django 5.0 on 2024-01-30 20:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("travel", "0006_alter_travel_profile_preffered_airports_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Airport_suitability",
            new_name="Suitable_airport",
        ),
        migrations.CreateModel(
            name="Profile_destinations",
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
                (
                    "airport",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile_destinations",
                        to="travel.airport",
                    ),
                ),
                (
                    "travel_profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="destinations",
                        to="travel.travel_profile",
                    ),
                ),
            ],
        ),
    ]
