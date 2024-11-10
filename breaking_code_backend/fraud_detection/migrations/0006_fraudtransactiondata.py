# Generated by Django 5.1.1 on 2024-09-20 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fraud_detection', '0005_remove_transaction_created_at_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='FraudTransactionData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('account_number', models.CharField(blank=True, max_length=20, null=True)),
                ('vpa', models.CharField(blank=True, max_length=50, null=True)),
                ('origin_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('mcc', models.CharField(blank=True, max_length=4, null=True)),
                ('mode', models.CharField(max_length=10)),
                ('txns_id', models.BigIntegerField(blank=True, null=True)),
                ('merchant_id', models.IntegerField(blank=True, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('narration', models.TextField(blank=True, null=True)),
                ('device_id', models.CharField(blank=True, max_length=100, null=True)),
                ('pin_code', models.CharField(blank=True, max_length=6, null=True)),
                ('rules_broken', models.JSONField(blank=True, default=list, null=True)),
            ],
            options={
                'db_table': 'fraud_transaction_data',
                'managed': True,
            },
        ),
    ]