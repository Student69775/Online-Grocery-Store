# Generated by Django 5.1.3 on 2024-11-30 09:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0016_delete_ordersummary_delete_sale'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='order',
            table='products_order',
        ),
    ]