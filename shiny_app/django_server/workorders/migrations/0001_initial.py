# Generated by Django 4.2 on 2023-04-17 19:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("customers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Workorder",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ls_workorder_id", models.IntegerField(null=True)),
                ("time_in", models.DateTimeField(null=True)),
                ("eta_out", models.DateTimeField(null=True)),
                ("note", models.TextField(blank=True, null=True)),
                ("warranty", models.BooleanField(null=True)),
                ("tax", models.BooleanField(null=True)),
                ("archived", models.BooleanField(null=True)),
                ("create_time", models.DateTimeField(auto_now_add=True)),
                ("update_time", models.DateTimeField(auto_now=True)),
                ("update_from_ls_time", models.DateTimeField(null=True)),
                ("item_description", models.CharField(max_length=100, null=True)),
                (
                    "total",
                    models.DecimalField(decimal_places=2, max_digits=10, null=True),
                ),
                ("status", models.CharField(max_length=20, null=True)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="customers.customer",
                    ),
                ),
            ],
        ),
    ]
