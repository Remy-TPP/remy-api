# Generated by Django 3.0.8 on 2020-07-22 20:41

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_auto_20200720_1743'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dish',
            options={'verbose_name_plural': 'dishes'},
        ),
        migrations.AlterModelOptions(
            name='dishcategory',
            options={'verbose_name_plural': 'dish categories'},
        ),
        migrations.AlterModelOptions(
            name='dishlabel',
            options={'verbose_name_plural': 'dish labels'},
        ),
        migrations.AddField(
            model_name='dish',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='dish',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='recipe',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='recipe',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
