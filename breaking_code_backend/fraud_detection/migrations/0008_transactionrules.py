# Generated by Django 5.1.1 on 2024-09-21 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fraud_detection', '0007_fraudtransactiondata_created_date_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransactionRules',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_date', models.DateTimeField(auto_now=True, null=True)),
                ('deleted_at', models.DateTimeField(blank=True, default=None, null=True)),
                ('rule_id', models.AutoField(primary_key=True, serialize=False)),
                ('merchant_id', models.IntegerField(blank=True, null=True)),
                ('sql_query', models.TextField(blank=True, null=True)),
                ('rule_score', models.IntegerField(blank=True, default=0, null=True)),
                ('rule_description', models.TextField(blank=True, null=True)),
                ('rule_title', models.CharField(blank=True, max_length=255, null=True)),
                ('fraud_entity', models.CharField(blank=True, max_length=50, null=True)),
                ('fraud_type', models.CharField(choices=[('TRANSACTION_VELOCITY', 'Transaction Velocity'), ('NEGATIVE_LIST', 'Negative List'), ('GMV_LIMIT_EXCEEDED', 'GMV Limit Exceeded'), ('SUSPICIOUS_IP', 'Suspicious IP Address'), ('DEVICE_FRAUD', 'Device Fraud'), ('CARD_FRAUD', 'Card Fraud'), ('MULTIPLE_TXNS', 'Multiple Transactions in Short Time')], max_length=50)),
            ],
            options={
                'db_table': 'transaction_rules',
                'managed': True,
            },
        ),
    ]
