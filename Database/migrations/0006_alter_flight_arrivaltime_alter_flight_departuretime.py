# Generated by Django 5.0.4 on 2024-05-11 15:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Database", "0005_alter_flight_arrivaltime_alter_flight_departuretime"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flight",
            name="arrivalTime",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="flight",
            name="departureTime",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
