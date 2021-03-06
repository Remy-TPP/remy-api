# Generated by Django 3.0.8 on 2020-07-20 17:43

import apps.recipes.models
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_recipe_ingredients'),
    ]

    operations = [
        migrations.CreateModel(
            name='DishCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('description', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='DishLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
            ],
        ),
        migrations.CreateModel(
            name='RecipeInstructions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('steps', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), default=list, size=None)),
            ],
        ),
        migrations.AlterField(
            model_name='recipe',
            name='title',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.CreateModel(
            name='Dish',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('description', models.TextField()),
                ('categories', models.ManyToManyField(to='recipes.DishCategory')),
                ('labels', models.ManyToManyField(to='recipes.DishLabel')),
            ],
        ),
        migrations.AddField(
            model_name='recipe',
            name='dish',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recipes', to='recipes.Dish'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='instructions',
            field=models.OneToOneField(default=apps.recipes.models.RecipeInstructions.default, on_delete=django.db.models.deletion.CASCADE, to='recipes.RecipeInstructions'),
        ),
    ]
