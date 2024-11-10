from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Helper functions
def condition_to_sql(condition):
    """
    Recursively converts a condition dictionary to a SQL WHERE clause string.
    """
    if 'logic' in condition:
        logic = condition['logic'].upper()
        sub_conditions = condition['conditions']
        sql_fragments = []
        for sub_condition in sub_conditions:
            sql_fragment = condition_to_sql(sub_condition)
            sql_fragments.append(f'({sql_fragment})')
        return f' {logic} '.join(sql_fragments)
    else:
        field = condition['field']
        operator = condition['operator'].upper()
        value = condition['value']

        if operator == 'IN' and isinstance(value, list):
            value_list = ', '.join(f"{v}" if isinstance(v, str) else str(v) for v in value)
            value_formatted = f"({value_list})"
        elif isinstance(value, str):
            value_formatted = f"{value}"
        else:
            value_formatted = str(value)

        return f"{field} {operator} {value_formatted}"

def generate_sql_query(condition, table_name='', select_clause='*'):
    """
    Generates a complete SQL query from the given condition.
    Uses custom SELECT clause if provided, defaults to *.
    """
    print("HERE")
    print("SELECT clouse", select_clause)
    where_clause = condition_to_sql(condition)
    sql_query = f"SELECT {select_clause} FROM EbzTxnsTopic WHERE {where_clause}"
    return sql_query

# API View function
# @csrf_exempt
# def generate_sql(request):
#     if request.method == 'POST':
#         try:
#             data = json.loads(request.body)
#             condition = data.get('condition', {})
#             table_name = data.get('table_name', 'transactions')

#             if condition:
#                 sql_query = generate_sql_query(condition, table_name)
#                 return JsonResponse({'sql_query': sql_query}, status=200)
#             else:
#                 return JsonResponse({'error': 'Condition data missing or invalid'}, status=400)
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON format'}, status=400)
#     else:
#         return JsonResponse({'error': 'Invalid request method'}, status=405)



# SELECT  CASE WHEN COALESCE(sum(amount), 0) > CAST(LOOKUP('-1', 'GMVLookupTable') AS DOUBLE) THEN TRUE ELSE FALSE END AS is_greater_than_lookup FROM EbzTxnsTopic WHERE ((TIMESTAMP_TO_MILLIS("__time") >= (TIMESTAMP_TO_MILLIS(CURRENT_TIMESTAMP) - CAST(LOOKUP('-1', 'shortTimePeriodLookupTable') AS BIGINT)*1000)))



# SELECT  CASE WHEN COALESCE(sum(amount), 0) > CAST(LOOKUP('-1', 'GMVLookupTable') AS DOUBLE) THEN TRUE ELSE FALSE END AS is_greater_than_lookup FROM transactions WHERE ((TIMESTAMP_TO_MILLIS("__time") >= '(TIMESTAMP_TO_MILLIS(CURRENT_TIMESTAMP) - CAST(LOOKUP('-1', 'shortTimePeriodLookupTable') AS BIGINT)*1000)'));