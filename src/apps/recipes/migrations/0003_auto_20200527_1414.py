# Generated by Django 3.0.2 on 2020-05-27 14:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20200527_1404'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='amount',
            name='weight',
            field=models.FloatField(),
        ),
        migrations.DeleteModel(
            name='Weight',
        ),
        migrations.AlterField(
            model_name='amount',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Unit'),
        ),
    ]
