# Generated by Django 4.2.5 on 2023-09-17 15:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0019_alter_productvariation_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productvariation',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='product_variation', to='products.product'),
        ),
    ]
