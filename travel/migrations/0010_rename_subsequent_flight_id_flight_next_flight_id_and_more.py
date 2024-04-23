# Generated by Django 5.0 on 2024-02-04 21:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("travel", "0009_flight_subsequent_flight_id_travel_offer"),
    ]

    operations = [
        migrations.RenameField(
            model_name="flight",
            old_name="subsequent_flight_id",
            new_name="next_flight_id",
        ),
        migrations.AddField(
            model_name="flight",
            name="identifier",
            field=models.CharField(default="", max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="flight",
            name="previous_flight_id",
            field=models.IntegerField(default=None),
        ),
    ]
