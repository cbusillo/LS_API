# Generated by Django 4.2 on 2023-04-20 04:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("customers", "0002_alter_customer_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customer",
            name="ls_customer_id",
            field=models.IntegerField(db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name="customer",
            name="update_from_ls_time",
            field=models.DateTimeField(db_index=True, null=True),
        ),
    ]
