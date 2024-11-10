# serializers.py
from rest_framework import serializers
from fraud_detection.models.txn_rules import TransactionRules

class TransactionRulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionRules
        fields = ['merchant_id', 'sql_query', 'rule_score', 'rule_description', 'rule_title']
