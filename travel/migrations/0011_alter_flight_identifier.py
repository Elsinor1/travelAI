# Generated by Django 5.0 on 2024-02-04 21:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("travel", "0010_rename_subsequent_flight_id_flight_next_flight_id_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flight",
            name="identifier",
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
