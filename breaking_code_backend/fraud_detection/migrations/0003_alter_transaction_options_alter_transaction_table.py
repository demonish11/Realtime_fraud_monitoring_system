# Generated by Django 5.1.1 on 2024-09-19 09:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fraud_detection', '0002_alter_transaction_amount_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='transaction',
            options={'managed': True},
        ),
        migrations.AlterModelTable(
            name='transaction',
            table='transaction',
        ),
    ]