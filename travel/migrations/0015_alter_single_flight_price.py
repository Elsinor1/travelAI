# Generated by Django 5.0 on 2024-02-23 18:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("travel", "0014_remove_profile_destination_airport_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="single_flight",
            name="price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=6, null=True
            ),
        ),
    ]
