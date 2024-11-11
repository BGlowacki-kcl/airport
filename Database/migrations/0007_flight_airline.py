# Generated by Django 5.0.4 on 2024-05-23 15:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Database", "0006_alter_flight_arrivaltime_alter_flight_departuretime"),
    ]

    operations = [
        migrations.AddField(
            model_name="flight",
            name="airline",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="Database.airline",
            ),
        ),
    ]
