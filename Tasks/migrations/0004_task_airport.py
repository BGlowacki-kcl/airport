# Generated by Django 5.0.4 on 2024-06-09 13:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Database", "0008_ticket_price"),
        ("Tasks", "0003_remove_task_duedate"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="airport",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="Database.airport",
            ),
        ),
    ]
