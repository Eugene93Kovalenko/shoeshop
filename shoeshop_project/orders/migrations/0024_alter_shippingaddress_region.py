# Generated by Django 4.2.5 on 2023-10-16 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0023_shippingaddress_region'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingaddress',
            name='region',
            field=models.CharField(max_length=100),
        ),
    ]
