# Generated by Django 4.2.5 on 2023-09-05 19:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='size',
            name='name',
            field=models.PositiveIntegerField(max_length=2),
        ),
    ]
