# Generated by Django 3.0.9 on 2020-08-27 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0017_auto_20200826_1928'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='quantity',
            field=models.DecimalField(decimal_places=5, max_digits=12, null=True),
        ),
    ]
