# Generated by Django 3.0.2 on 2020-06-02 15:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0006_auto_20200527_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='substitutions',
            field=models.ManyToManyField(blank=True, null=True, related_name='_ingredient_substitutions_+', to='recipes.Ingredient'),
        ),
    ]
