def condition_to_sql(condition):
    """
    Recursively converts a condition dictionary to a SQL WHERE clause string.
    """
    if 'logic' in condition:
        # It's a group of conditions (AND/OR)
        logic = condition['logic'].upper()
        sub_conditions = condition['conditions']
        sql_fragments = []
        for sub_condition in sub_conditions:
            sql_fragment = condition_to_sql(sub_condition)
            sql_fragments.append(f'({sql_fragment})')
        return f' {logic} '.join(sql_fragments)
    else:
        # It's a simple condition
        field = condition['field']
        operator = condition['operator'].upper()
        value = condition['value']

        # Handle different types of values
        if operator == 'IN' and isinstance(value, list):
            value_list = ', '.join(f"'{v}'" if isinstance(v, str) else str(v) for v in value)
            value_formatted = f"({value_list})"
        elif isinstance(value, str):
            value_formatted = f"'{value}'"
        else:
            value_formatted = str(value)

        return f"{field} {operator} {value_formatted}"

def generate_sql_query(condition, table_name='transactions'):
    """
    Generates a complete SQL query from the given condition.
    """
    where_clause = condition_to_sql(condition)
    sql_query = f"SELECT * FROM {table_name} WHERE {where_clause};"
    return sql_query

# Example nested condition
nested_condition = {
    'logic': 'OR',
    'conditions': [
        {
            'logic': 'AND',
            'conditions': [
                {'field': 'amount', 'operator': '>', 'value': "LOOKUP(420,'mid_lookup_table')"},
                {
                    'logic': 'OR',
                    'conditions': [
                        {'field': 'country', 'operator': '=', 'value': "LOOKUP(default,'account_number_lookup_table')"},
                        {'field': 'country', 'operator': 'IN', 'value': ["LOOKUP(default,'mid_lookup_table')", "LOOKUP(default,'mid_lookup_table')"]}
                    ]
                },
            
            ]
        },
        {'field': 'name', 'operator': '>', 'value': 1000},

    ]
}

#default
#COALESCE(LOOKUP(default,'mid_lookup_table'), LOOKUP('default','mid_lookup_table'))

# (cond1) and (cond2 or cond3) or (cond5 and (cond)) # 
# Generate SQL
if __name__ == "__main__":
    sql_query = generate_sql_query(nested_condition)
    print("Generated SQL Query:")
    print(sql_query)



# Table 
# merchant_id , sql query
# *,  SELECT * FROM transactions WHERE (amount > 1000) AND ((country = 'US') OR (country IN ('CA', 'MX')));
# 120, SELECT * FROM transactions WHERE (amount > 1000) AND ((country = 'US') OR (country IN ('CA', 'MX')));


# SELECT * FROM transactions WHERE ((amount > 1000) AND ((country = 'US') OR (country IN ('CA', 'MX')))) OR( name = "abc");




# Rule added:-

# # MID drop down(opt)
# # default
# # Mid num:- 420


# submit btn 