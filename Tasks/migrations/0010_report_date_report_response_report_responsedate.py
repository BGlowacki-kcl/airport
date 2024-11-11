# Generated by Django 5.0.4 on 2024-06-10 10:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Tasks", "0009_report_issue_alter_task_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="report",
            name="date",
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name="report",
            name="response",
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
        migrations.AddField(
            model_name="report",
            name="responseDate",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]