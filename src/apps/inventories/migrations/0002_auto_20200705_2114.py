# Generated by Django 3.0.2 on 2020-07-05 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0008_manually_fix'),
        ('inventories', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='place',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='places', to='profiles.Profile'),
        ),
    ]