# Generated by Django 4.2 on 2023-05-22 19:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("customers", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Item",
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
                (
                    "ls_item_id",
                    models.IntegerField(db_index=True, null=True, unique=True),
                ),
                (
                    "default_cost",
                    models.DecimalField(decimal_places=2, max_digits=10, null=True),
                ),
                (
                    "average_cost",
                    models.DecimalField(decimal_places=4, max_digits=12, null=True),
                ),
                (
                    "price",
                    models.DecimalField(decimal_places=2, max_digits=10, null=True),
                ),
                ("tax", models.BooleanField(null=True)),
                ("archived", models.BooleanField(null=True)),
                ("item_type", models.CharField(max_length=20, null=True)),
                ("serialized", models.BooleanField(null=True)),
                ("description", models.CharField(max_length=255)),
                ("model_year", models.IntegerField(null=True)),
                ("upc", models.CharField(blank=True, max_length=20, null=True)),
                ("custom_sku", models.CharField(blank=True, max_length=20, null=True)),
                ("manufacturer_sku", models.CharField(max_length=20, null=True)),
                ("create_time", models.DateTimeField(auto_now_add=True)),
                ("update_time", models.DateTimeField(auto_now=True)),
                ("update_from_ls_time", models.DateTimeField(db_index=True, null=True)),
                ("item_matrix_id", models.IntegerField(null=True)),
                ("sizes", models.TextField(max_length=300, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Serial",
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
                (
                    "ls_serial_id",
                    models.IntegerField(db_index=True, null=True, unique=True),
                ),
                ("value_1", models.CharField(max_length=255, null=True)),
                ("value_2", models.CharField(max_length=255, null=True)),
                ("serial_number", models.CharField(max_length=50, null=True)),
                ("description", models.CharField(max_length=255, null=True)),
                ("create_time", models.DateTimeField(auto_now_add=True)),
                ("update_time", models.DateTimeField(auto_now=True)),
                ("update_from_ls_time", models.DateTimeField(db_index=True, null=True)),
                (
                    "customer",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="serials",
                        to="customers.customer",
                    ),
                ),
                (
                    "item",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="serials",
                        to="items.item",
                    ),
                ),
            ],
        ),
    ]
