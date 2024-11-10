from rest_framework import serializers
from fraud_detection.models.txn_rules import TransactionRules

class TransactionRulesDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionRules
        fields = '__all__'
