# Generated by Django 5.0.4 on 2024-06-06 20:03

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("Tasks", "0002_approval_taskstodo"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="task",
            name="dueDate",
        ),
    ]