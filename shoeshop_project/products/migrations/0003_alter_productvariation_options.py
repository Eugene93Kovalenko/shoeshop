# Generated by Django 4.2.5 on 2024-03-24 11:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_remove_product_slug'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='productvariation',
            options={'ordering': ['size__name'], 'verbose_name': 'Product | Size', 'verbose_name_plural': 'Product | Size'},
        ),
    ]