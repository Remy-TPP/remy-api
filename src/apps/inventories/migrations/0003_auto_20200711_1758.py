# Generated by Django 3.0.2 on 2020-07-11 17:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_auto_20200722_2041'),
        ('inventories', '0002_auto_20200705_2114'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventory',
            name='products',
            field=models.ManyToManyField(through='inventories.InventoryItem', to='products.Product'),
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='amount',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='products.Amount'),
        ),
    ]
