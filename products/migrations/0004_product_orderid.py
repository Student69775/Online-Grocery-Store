# Generated by Django 4.0.6 on 2024-02-05 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_auto_20210426_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='orderid',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]