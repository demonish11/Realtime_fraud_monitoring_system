# models.py

from django.db import models
from fraud_detection.models.base_model import BaseModel

class Transaction(BaseModel):
    account_number = models.CharField(max_length=50, null=True, blank=True)
    vpa = models.CharField(max_length=100, null=True, blank=True)  # Virtual Payment Address
    origin_ip = models.GenericIPAddressField(null=True, blank=True)
    mcc = models.CharField(max_length=4, null=True, blank=True)  # Merchant Category Code
    mode = models.CharField(max_length=20, choices=[('UPI', 'UPI'), ('NEFT', 'NEFT'), ('RTGS', 'RTGS')])
    txn_id = models.BigIntegerField(null=True, blank=True, db_index=True)  # Transaction ID
    merchant_id = models.IntegerField(null=True, blank=True)
    amount = models.DecimalField(null=True, blank=True, max_digits=12, decimal_places=2)
    narration = models.TextField(null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'transaction'
