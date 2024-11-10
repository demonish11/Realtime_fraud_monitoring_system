from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from decimal import Decimal
from fraud_detection.models import Transaction
from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv4_address, validate_ipv6_address
from fraud_detection.controller.rule_breaker_controller import generate_sql_query
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def generate_sql(request):
    if request.method == 'POST':
        try:
            # Parse the request body
            body = json.loads(request.body)

            # Extract relevant fields from the request
            condition = body.get('condition', {})
            table_name = body.get('table_name', 'transactions')
            select_clause = body.get('select_clause', '*')  # Default to * if no select clause provided

            # Generate the SQL query
            sql_query = generate_sql_query(condition, table_name, select_clause)

            return JsonResponse({'sql_query': sql_query}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST method is allowed.'}, status=405)


@api_view(['POST'])
def transaction(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        try:
            # Validate IP address
            origin_ip = data.get('origin_ip')
            if origin_ip:
                try:
                    validate_ipv4_address(origin_ip)
                except ValidationError:
                    try:
                        validate_ipv6_address(origin_ip)
                    except ValidationError:
                        return JsonResponse({"status": "error", "message": "Invalid IP address format"})
            
            txn_id = int(data.get('txns_id')) if data.get('txns_id') else None
            merchant_id = int(data.get('merchant_id')) if data.get('merchant_id') else None
            amount = Decimal(data.get('amount')) if data.get('amount') else None
            
            # Create a new Transaction object and save it to the database
            transaction = Transaction.objects.create(
                account_number=data.get('account_number'),
                vpa=data.get('vpa'),
                origin_ip=origin_ip,
                mcc=data.get('mcc'),
                mode=data.get('mode'),
                txn_id=txn_id,
                merchant_id=merchant_id,
                amount=amount,
                narration=data.get('narration'),
                device_id=data.get('device_id'),
                pin_code=data.get('pin_code')
            )
            
            return JsonResponse({"status": "success", "message": "Transaction saved successfully"})
        
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    
    return JsonResponse({"status": "error", "message": "Invalid request"})



from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from .models import FraudTransactionData, TransactionRules
from fraud_detection.serializers.fraud_txn_data_serializer import FraudTransactionDataSerializer
from fraud_detection.serializers.txn_rules_data_serializer import TransactionRulesDataSerializer
from fraud_detection.serializers.txn_rules_serializer import TransactionRulesSerializer

class CustomPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100

class FraudTransactionDataList(generics.ListAPIView):
    queryset = FraudTransactionData.objects.all().order_by('-updated_date')
    serializer_class = FraudTransactionDataSerializer
    pagination_class = CustomPagination

class TxnRulesDataList(generics.ListAPIView):
    queryset = TransactionRules.objects.all().order_by('-updated_date')
    serializer_class = TransactionRulesDataSerializer
    pagination_class = CustomPagination


@api_view(['POST'])
def submit_rule(request):
    data = request.data
    rule = TransactionRules(
        sql_query=data.get('sql_query'),
        rule_score=data.get('rule_score'),
        rule_description=data.get('rule_description'),
        rule_title=data.get('rule_title'),
        merchant_id=data.get('merchant_id'),
        fraud_entity=data.get('fraud_entity'),  # Capture Fraud Entity
        fraud_type=data.get('fraud_type'),      # Capture Fraud Type
    )
    rule.save()
    return JsonResponse({'message': 'Rule submitted successfully!'}, status=200)
