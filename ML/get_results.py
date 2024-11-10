import tensorflow as tf
import numpy as np
import json
import logging
import psycopg2  # PostgreSQL library to connect to RDS
from confluent_kafka import Consumer  # Kafka Consumer

# Configure logging to save logs of fraudulent transactions to a file
logging.basicConfig(filename='fraud_detection.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Step 1: Connect to the PostgreSQL RDS instance using the provided Django-style credentials
conn_rds = psycopg2.connect(
    host="breaking-code-1.cjisqek2oox2.ap-south-1.rds.amazonaws.com",  # Your RDS endpoint
    database="breaking_code",  # Your database name
    user="postgres",  # Your username
    password="Root#123",  # Replace with your PostgreSQL password
    port="5432"
)

# Create a cursor object to interact with the PostgreSQL database
cursor_rds = conn_rds.cursor()

# List of known fraud hotspot pin codes
fraud_hotspots = ['815351', '815352', '815353', '122107', '122108']  # Fraud-prone areas

# Step 2: Preprocess the transaction data before passing it to the model
def preprocess_transaction(transaction):
    """
    Preprocess transaction data for fraud detection.
    Ensure account_number, merchant_id, and pin_code are passed as strings (as expected by the model).
    """
    try:
        # Convert amount to float
        transaction['amount'] = float(transaction['amount'])  
        
        # Flag high-value transactions
        transaction['high_value_txn'] = 1 if transaction['amount'] > 100000 else 0  
        
        # Count rule violations
        transaction['rule_violation_count'] = len(transaction.get('rules_broken', []))  
        
        # Flag fraud hotspots based on pin codes
        transaction['fraud_hotspot'] = 1 if transaction['pin_code'] in fraud_hotspots else 0

        # Ensure account_number, merchant_id, and pin_code are strings (as expected by the model)
        account_number_str = str(transaction['account_number'])
        merchant_id_str = str(transaction['merchant_id'])
        pin_code_str = str(transaction['pin_code'])

        # Return processed transaction values as a list
        return [account_number_str, merchant_id_str, pin_code_str, 
                transaction['amount'], transaction['rule_violation_count'], transaction['fraud_hotspot']]
    
    except Exception as e:
        logging.error(f"Error processing transaction: {transaction}, Error: {e}")
        return None  # Skip if processing fails

# Step 3: Load the pre-trained model
model = tf.keras.models.load_model('fraud_detection_model_with_embeddings.h5')  # Load the pre-trained model
print("Model loaded successfully!")

# Step 4: Initialize the Kafka consumer to read from the 'fraud_transaction_data' topic
consumer = Consumer({
    'bootstrap.servers': 'ip-172-31-13-38.ap-south-1.compute.internal:9092',  # Kafka broker IP
    'group.id': 'fraud-detection-group_2',  # New Consumer group name
    'auto.offset.reset': 'earliest'  # Start reading from the earliest message
})

consumer.subscribe(['fraud_transaction_data'])  # Replace with your Kafka topic

# Step 5: Start real-time fraud detection with Kafka and the loaded model
print("Starting real-time fraud detection...")

try:
    while True:
        msg = consumer.poll(1.0)  # Wait for 1 second for new messages
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        # Decode the Kafka message
        transaction = json.loads(msg.value().decode('utf-8'))
        
        # Check if the transaction ID exists in the database before processing
        cursor_rds.execute('SELECT txns_id FROM public.fraud_detection WHERE txns_id = %s', (transaction['txns_id'],))
        result = cursor_rds.fetchone()

        if result:
            # Preprocess the transaction
            processed_txn = preprocess_transaction(transaction)
            if processed_txn is None:
                continue  # Skip if transaction processing failed

            # Convert preprocessed data into numpy array format, ensuring proper dtype and shape
            account_number_array = np.array([processed_txn[0]], dtype=object)  # account_number (object dtype for strings)
            merchant_id_array = np.array([processed_txn[1]], dtype=object)     # merchant_id (object dtype for strings)
            pin_code_array = np.array([processed_txn[2]], dtype=object)        # pin_code (object dtype for strings)
            fraud_hotspot_array = np.array([processed_txn[5]], dtype=np.float32)  # fraud_hotspot (float32)
            amount_array = np.array([processed_txn[3]], dtype=np.float32)         # amount (float32)
            rule_violation_array = np.array([processed_txn[4]], dtype=np.float32) # rule_violation_count (float32)

            # Perform prediction
            prediction = model.predict([
                account_number_array,
                merchant_id_array,
                pin_code_array,
                fraud_hotspot_array,
                amount_array,
                rule_violation_array
            ])

            # Convert numpy types to Python native types
            ml_score = float(prediction[0][0])  # Convert numpy.float32 to native Python float
            amount = float(transaction['amount'])  # Ensure amount is a native Python float
            pin_code = str(transaction['pin_code'])  # Ensure pin_code is a native string

            # Update the record in the PostgreSQL database with the ml_score
            cursor_rds.execute('''
                UPDATE public.fraud_detection
                SET ml_score = %s
                WHERE txns_id = %s
            ''', (ml_score, transaction['txns_id']))
            conn_rds.commit()  # Save to DB

            logging.info(f"Transaction {transaction['txns_id']} updated with ml_score: {ml_score}")
            print(f"Transaction {transaction['txns_id']} updated with ml_score: {ml_score}")
        else:
            print(f"No matching transaction for txns_id: {transaction['txns_id']} in the database.")

except KeyboardInterrupt:
    print("Stopping consumer...")
finally:
    consumer.close()
    cursor_rds.close()
    conn_rds.close()
