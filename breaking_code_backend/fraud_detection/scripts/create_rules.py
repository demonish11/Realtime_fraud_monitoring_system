from django.core.management.base import BaseCommand
from fraud_detection.models import TransactionRules

class Command(BaseCommand):
    help = 'Create dummy entries for TransactionRules'

    def handle(self, *args, **kwargs):
        dummy_rules = [
            {
                'merchant_id': 4486,
                'sql_query': "SELECT * FROM transactions WHERE ((account_number = '1111') AND (amount = '100'))",
                'rule_score': 85,
                'rule_description': 'Rule for monitoring specific account with a fixed amount.',
                'rule_title': 'Fixed Amount Transaction',
                'fraud_entity': 'Account Number',
                'fraud_type': 'TRANSACTION_VELOCITY'
            },
            {
                'merchant_id': 4486,
                'sql_query': "SELECT * FROM transactions WHERE ((ip_address = '192.168.1.1') AND (amount > '500'))",
                'rule_score': 90,
                'rule_description': 'Detects transactions from suspicious IP addresses exceeding a limit.',
                'rule_title': 'Suspicious IP Transactions',
                'fraud_entity': 'IP Address',
                'fraud_type': 'SUSPICIOUS_IP'
            },
            {
                'merchant_id': 4486,
                'sql_query': "SELECT * FROM transactions WHERE ((device_id = 'device123') AND (timestamp > NOW() - INTERVAL '1 hour'))",
                'rule_score': 75,
                'rule_description': 'Identifies multiple transactions from the same device within a short time.',
                'rule_title': 'Device Fraud Detection',
                'fraud_entity': 'Device ID',
                'fraud_type': 'MULTIPLE_TXNS'
            },
            {
                'merchant_id': 4486,
                'sql_query': "SELECT * FROM transactions WHERE ((amount > '1000') AND (status = 'failed'))",
                'rule_score': 80,
                'rule_description': 'Monitors failed high-value transactions.',
                'rule_title': 'High-Value Failed Transactions',
                'fraud_entity': 'Transaction Amount',
                'fraud_type': 'CARD_FRAUD'
            },
            {
                'merchant_id': 4486,
                'sql_query': "SELECT * FROM transactions WHERE ((account_number IN (SELECT account_number FROM negative_list)))",
                'rule_score': 95,
                'rule_description': 'Blocks transactions from accounts in the negative list.',
                'rule_title': 'Negative List Check',
                'fraud_entity': 'Account Number',
                'fraud_type': 'NEGATIVE_LIST'
            },
        ]

        for rule in dummy_rules:
            TransactionRules.objects.create(**rule)

        self.stdout.write(self.style.SUCCESS('Successfully created dummy entries for TransactionRules'))
