# Generated by Django 3.0.9 on 2020-08-17 13:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventories', '0005_auto_20200816_2144'),
        ('profiles', '0009_auto_20200730_0617'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=300, null=True)),
                ('starting_datetime', models.DateTimeField()),
                ('finishing_datetime', models.DateTimeField()),
                ('only_host_inventory', models.BooleanField(default=True)),
                ('attendees', models.ManyToManyField(blank=True, related_name='events', to='profiles.Profile')),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hosted_events', to='profiles.Profile')),
                ('place', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='inventories.Place')),
            ],
        ),
        migrations.DeleteModel(
            name='Group',
        ),
    ]
