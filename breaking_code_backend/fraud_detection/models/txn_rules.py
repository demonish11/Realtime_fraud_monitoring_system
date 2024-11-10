from django.db import models
from fraud_detection.models.base_model import BaseModel

FRAUD_TYPE_CHOICES = [
        ('TRANSACTION_VELOCITY', 'Transaction Velocity'),
        ('NEGATIVE_LIST', 'Negative List'),
        ('GMV_LIMIT_EXCEEDED', 'GMV Limit Exceeded'),
        ('SUSPICIOUS_IP', 'Suspicious IP Address'),
        ('DEVICE_FRAUD', 'Device Fraud'),
        ('CARD_FRAUD', 'Card Fraud'),
        ('MULTIPLE_TXNS', 'Multiple Transactions in Short Time'),
    ]

class TransactionRules(BaseModel):
    merchant_id = models.IntegerField(null=True, blank=True, default=-1)  # Foreign key to the merchant (adjust as needed)
    sql_query = models.TextField(null=True, blank=True)  # Store the SQL query
    rule_score = models.IntegerField(default=0, null=True, blank=True)  # Score between 0-100
    rule_id = models.AutoField(primary_key=True, blank=True)  # Auto-incrementing rule ID
    rule_description = models.TextField(null=True, blank=True)  # Description of the rule
    rule_title = models.CharField(max_length=255, null=True, blank=True)  # Title of the rule
    fraud_entity = models.CharField(max_length=50, null=True, blank=True)
    fraud_type = models.CharField(max_length=50, choices=FRAUD_TYPE_CHOICES)  # Fraud type

    class Meta:
        managed = True
        db_table = 'transaction_rules'

