from rest_framework import serializers
from fraud_detection.models.fraud_transaction import FraudTransactionData

class FraudTransactionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = FraudTransactionData
        fields = '__all__'
