# Generated by Django 5.1.1 on 2024-09-13 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("borrowing", "0002_alter_borrowing_actual_return_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="borrowing",
            name="actual_return_date",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
