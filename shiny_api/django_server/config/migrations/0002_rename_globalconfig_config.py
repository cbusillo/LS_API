# Generated by Django 4.2 on 2023-04-08 19:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("config", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="GlobalConfig",
            new_name="Config",
        ),
    ]
