# Generated by Django 5.0.4 on 2024-06-09 17:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Tasks", "0006_task_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="ifHidden",
            field=models.BooleanField(default=False),
        ),
    ]