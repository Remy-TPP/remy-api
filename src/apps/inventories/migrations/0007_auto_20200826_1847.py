# Generated by Django 3.0.9 on 2020-08-26 18:47

import apps.products.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20200722_2041'),
        ('inventories', '0006_auto_20200818_2254'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventoryitem',
            name='amount',
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='quantity',
            field=models.DecimalField(decimal_places=5, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='unit',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='products.Unit'),
        ),
    ]