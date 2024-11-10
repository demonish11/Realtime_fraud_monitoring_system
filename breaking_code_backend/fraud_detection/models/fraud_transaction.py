from django.db import models
from decimal import Decimal
import json
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


class FraudTransactionData(BaseModel):
    account_number = models.CharField(max_length=20, null=True, blank=True)
    vpa = models.CharField(max_length=50, null=True, blank=True)  # Virtual Payment Address
    origin_ip = models.GenericIPAddressField(null=True, blank=True)
    mcc = models.CharField(max_length=4, null=True, blank=True)  # Merchant Category Code
    mode = models.CharField(max_length=10)  # UPI, NEFT, etc.
    txns_id = models.BigIntegerField(null=True, blank=True)  # Transaction ID
    merchant_id = models.IntegerField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    narration = models.TextField(null=True, blank=True)
    device_id = models.CharField(max_length=100, null=True, blank=True)
    pin_code = models.CharField(max_length=6, null=True, blank=True)
    rules_broken = models.JSONField(default=list, null=True, blank=True)
    ml_score = models.CharField(max_length=50, null=True, blank=True, default=0)

    class Meta:
        managed = True
        db_table = 'fraud_transaction_data'

