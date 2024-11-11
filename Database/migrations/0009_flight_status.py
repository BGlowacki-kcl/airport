# Generated by Django 5.0.4 on 2024-06-18 06:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("Database", "0008_ticket_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="flight",
            name="status",
            field=models.CharField(
                choices=[
                    ("Before", "Before"),
                    ("During", "During"),
                    ("After", "After"),
                ],
                default="Before",
                max_length=10,
            ),
        ),
    ]