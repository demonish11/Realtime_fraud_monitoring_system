from django.urls import path

from . import views
from .views import FraudTransactionDataList, TxnRulesDataList

urlpatterns = [
    path("transaction/", views.transaction, name="transaction"),
    path('api/fraud-transactions/', FraudTransactionDataList.as_view(), name='fraud_transaction_list'),
    path('api/transaction-rules/', TxnRulesDataList.as_view(), name='fraud_transaction_list'),
    path('api/generate-sql/', views.generate_sql, name='generate_sql'),
    path('api/submit-rule/', views.submit_rule, name='submit-rule'),
]