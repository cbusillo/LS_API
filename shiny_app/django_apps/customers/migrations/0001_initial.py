# Generated by Django 4.2 on 2023-04-26 18:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Customer",
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
                    "ls_customer_id",
                    models.IntegerField(db_index=True, null=True, unique=True),
                ),
                ("first_name", models.CharField(max_length=100, null=True)),
                ("last_name", models.CharField(max_length=100, null=True)),
                ("title", models.CharField(blank=True, max_length=30, null=True)),
                ("company", models.CharField(blank=True, max_length=100, null=True)),
                ("create_time", models.DateTimeField(auto_now_add=True)),
                ("update_time", models.DateTimeField(auto_now=True)),
                ("update_from_ls_time", models.DateTimeField(db_index=True, null=True)),
                ("archived", models.BooleanField(null=True)),
                ("contact_id", models.IntegerField(null=True)),
                ("credit_account_id", models.IntegerField(blank=True, null=True)),
                ("customer_type_id", models.IntegerField(null=True)),
                ("tax_category_id", models.IntegerField(blank=True, null=True)),
                ("is_modified", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Phone",
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
                ("number", models.CharField(max_length=20)),
                ("number_type", models.CharField(max_length=20)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="phones",
                        to="customers.customer",
                    ),
                ),
            ],
            options={
                "unique_together": {("number", "customer", "number_type")},
            },
        ),
        migrations.CreateModel(
            name="Email",
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
                ("address", models.EmailField(max_length=254)),
                ("address_type", models.CharField(max_length=100)),
                (
                    "customer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="emails",
                        to="customers.customer",
                    ),
                ),
            ],
            options={
                "unique_together": {("address", "customer", "address_type")},
            },
        ),
    ]
