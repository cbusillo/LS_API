# Generated by Django 4.2 on 2023-04-30 19:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("sales", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="saleline",
            name="sale",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="sale_lines",
                to="sales.sale",
            ),
        ),
    ]
