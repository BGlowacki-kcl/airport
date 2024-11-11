# Generated by Django 5.0.4 on 2024-06-19 19:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Database", "0009_flight_status"),
        ("Tasks", "0012_pilotmessage_pilotconversation"),
    ]

    operations = [
        migrations.AddField(
            model_name="pilotmessage",
            name="answerToFlight",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="answer_to_flight",
                to="Database.flight",
            ),
        ),
    ]