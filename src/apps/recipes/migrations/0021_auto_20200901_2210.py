# Generated by Django 3.0.9 on 2020-09-01 22:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0020_auto_20200901_1552'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(null=True, upload_to='images/recipes'),
        ),
    ]
