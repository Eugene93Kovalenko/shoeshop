# Generated by Django 4.2.5 on 2023-09-06 15:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_alter_product_category_alter_product_style'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SizeVariations',
            new_name='SizeVariation',
        ),
    ]
