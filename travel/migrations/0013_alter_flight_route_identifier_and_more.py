# Generated by Django 5.0 on 2024-02-04 22:18

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("travel", "0012_flight_route_alter_travel_offer_departure_flight_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flight_route",
            name="identifier",
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name="single_flight",
            name="identifier",
            field=models.CharField(blank=True, max_length=100, null=True, unique=True),
        ),
    ]
