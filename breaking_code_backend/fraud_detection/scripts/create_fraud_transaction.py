import random
from faker import Faker
from decimal import Decimal
from fraud_detection.models.fraud_transaction import FraudTransactionData

fake = Faker()

# Define possible rules that can be broken
def generate_random_rules(amount):
    rules = []
    
    # Example rules
    if amount > 1000:
        rules.append("Amount greater than 1000")
    if random.choice([True, False]):
        rules.append("Transaction from bad region")  # Simulate checking against a negative list
    if random.choice([True, False]):
        rules.append("IP address on negative list")
    if random.choice([True, False]):
        rules.append("Device ID on negative list")
    if random.choice([True, False]):
        rules.append("Frequent transactions from this account")  # Example for transaction velocity
    
    return rules

def create_dummy_fraud_transactions(num_records=100):
    for _ in range(num_records):
        amount = Decimal(random.uniform(1.0, 200000.0)).quantize(Decimal('0.01'))  # Random amount
        rules_broken = generate_random_rules(amount)  # Generate random rules based on the amount

        transaction = FraudTransactionData(
            account_number=fake.bban(),  # Random bank account number
            vpa=fake.email(),  # Random email as a VPA
            origin_ip=fake.ipv4(),  # Random IPv4 address
            mcc=str(random.randint(1000, 9999)),  # Random MCC
            mode=random.choice(['UPI', 'NEFT', 'IMPS', 'RTGS']),  # Random transaction mode
            txns_id=random.randint(1000000000, 9999999999),  # Random transaction ID
            merchant_id=random.randint(1, 1000),  # Random merchant ID
            amount=amount,  # Random amount
            narration=fake.sentence(),  # Random narration
            device_id=fake.uuid4(),  # Random UUID as device ID
            pin_code=fake.zipcode(),  # Random 6-digit pin code
            rules_broken=rules_broken  # Randomly generated rules
        )
        transaction.save()

if __name__ == "__main__":
    create_dummy_fraud_transactions()
