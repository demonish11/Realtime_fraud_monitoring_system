import tensorflow as tf
import numpy as np
import pandas as pd
import json
import logging
import psycopg2  # PostgreSQL library to connect to RDS
from confluent_kafka import Consumer  # Kafka Consumer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Configure logging to save logs of fraudulent transactions to a file
logging.basicConfig(filename='fraud_detection.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Step 1: Connect to the PostgreSQL RDS instance using psycopg2
conn_rds = psycopg2.connect(
    host="fraud-transaction.cjisqek2oox2.ap-south-1.rds.amazonaws.com",  # Your RDS endpoint
    database="postgres",  # Your database name
    user="Breakinguser",  # Your username
    password="Breaking_code123"  # Replace with your PostgreSQL password
)

# Create a cursor object to interact with the PostgreSQL database
cursor_rds = conn_rds.cursor()

# List of known fraud hotspot pin codes
fraud_hotspots = ['815351', '815352', '815353', '122107', '122108']  # Fraud-prone areas

# Step 2: Preprocess the transaction data before passing it to the model
def preprocess_transaction(transaction):
    """
    Preprocess transaction data for fraud detection.
    """
    transaction['amount'] = float(transaction['amount'])  # Convert amount to float
    transaction['high_value_txn'] = 1 if transaction['amount'] > 100000 else 0  # Flag high-value transactions
    transaction['rule_violation_count'] = len(transaction.get('rules_broken', []))  # Count rule violations safely
    transaction['fraud_hotspot'] = 1 if transaction['pin_code'] in fraud_hotspots else 0  # Flag fraud hotspots

    # Generate a fraud label: consider a transaction fraudulent if it breaks multiple rules or is from a fraud hotspot
    transaction['is_fraudulent'] = 1 if transaction['rule_violation_count'] > 1 or transaction['fraud_hotspot'] == 1 else 0

    # Cast account_number, merchant_id, and pin_code to string, as required by the model
    account_number = str(transaction['account_number'])  # Convert to string
    merchant_id = str(transaction['merchant_id'])  # Convert to string
    pin_code = str(transaction['pin_code'])  # Convert to string

    # Return preprocessed transaction
    return [account_number, merchant_id, pin_code, transaction['amount'], transaction['rule_violation_count'], transaction['fraud_hotspot'], transaction['is_fraudulent']]

# Step 3: Define the fraud detection model
def build_model():
    """
    Build the TensorFlow model that includes embedding layers for categorical variables.
    """
    # Input layers (categorical features like account_number, merchant_id, and pin_code)
    account_input = tf.keras.layers.Input(shape=(1,), dtype='string', name='account_number')
    merchant_input = tf.keras.layers.Input(shape=(1,), dtype='string', name='merchant_id')
    pin_code_input = tf.keras.layers.Input(shape=(1,), dtype='string', name='pin_code')
    fraud_hotspot_input = tf.keras.layers.Input(shape=(1,), name='fraud_hotspot')
    amount_input = tf.keras.layers.Input(shape=(1,), name='amount')
    rule_violation_input = tf.keras.layers.Input(shape=(1,), name='rule_violation_count')

    # Embedding layers for categorical features
    account_hashed = tf.keras.layers.Hashing(num_bins=10000)(account_input)  # Hash the account number
    merchant_hashed = tf.keras.layers.Hashing(num_bins=1000)(merchant_input)  # Hash the merchant ID
    pin_code_hashed = tf.keras.layers.Hashing(num_bins=100000)(pin_code_input)  # Hash the pin code

    # Embedding layers based on hashed values
    account_embedding = tf.keras.layers.Embedding(input_dim=10000, output_dim=16)(account_hashed)
    merchant_embedding = tf.keras.layers.Embedding(input_dim=1000, output_dim=16)(merchant_hashed)
    pin_code_embedding = tf.keras.layers.Embedding(input_dim=100000, output_dim=16)(pin_code_hashed)

    # Flatten embeddings to pass them to dense layers
    account_flatten = tf.keras.layers.Flatten()(account_embedding)
    merchant_flatten = tf.keras.layers.Flatten()(merchant_embedding)
    pin_code_flatten = tf.keras.layers.Flatten()(pin_code_embedding)

    # Concatenate input layers
    concatenated = tf.keras.layers.Concatenate()([account_flatten, merchant_flatten, pin_code_flatten,
                                                  fraud_hotspot_input, amount_input, rule_violation_input])

    # Dense layers
    dense = tf.keras.layers.Dense(128, activation='relu')(concatenated)
    dense = tf.keras.layers.Dense(64, activation='relu')(dense)
    output = tf.keras.layers.Dense(1, activation='sigmoid')(dense)  # Output layer

    # Compile the model
    model = tf.keras.Model(inputs=[account_input, merchant_input, pin_code_input, fraud_hotspot_input,
                                   amount_input, rule_violation_input], outputs=output)
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    return model

# Step 4: Initialize the Kafka consumer
consumer = Consumer({
    'bootstrap.servers': 'ip-172-31-13-38.ap-south-1.compute.internal:9092',  # Kafka broker IP
    'group.id': 'fraud-detection-group_1',  # Consumer group name
    'auto.offset.reset': 'earliest'  # Start reading from the earliest message
})

consumer.subscribe(['ml_topic'])  # Replace with your Kafka topic

# Step 5: Collect real-time data from Kafka and train the model
data = []  # List to hold incoming transactions

print("Starting real-time fraud detection and data collection...")
try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        # Decode the Kafka message and append to the data list
        transaction = json.loads(msg.value().decode('utf-8'))
        data.append(preprocess_transaction(transaction))  # Preprocess each transaction

        # Stop collecting after a certain number of transactions (e.g., 10,000)
        if len(data) >= 100000:
            break

except KeyboardInterrupt:
    print("Stopping consumer...")
finally:
    consumer.close()

# Convert the collected data to a pandas DataFrame
df = pd.DataFrame(data, columns=['account_number', 'merchant_id', 'pin_code', 'amount',
                                 'rule_violation_count', 'fraud_hotspot', 'is_fraudulent'])

# Step 6: Preprocess the data for model training
X = df[['account_number', 'merchant_id', 'pin_code', 'amount', 'rule_violation_count', 'fraud_hotspot']]
y = df['is_fraudulent']  # Use the generated 'is_fraudulent' column as the target label

# Split into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize numerical features
scaler = StandardScaler()
X_train[['amount', 'rule_violation_count']] = scaler.fit_transform(X_train[['amount', 'rule_violation_count']])
X_test[['amount', 'rule_violation_count']] = scaler.transform(X_test[['amount', 'rule_violation_count']])

# Step 7: Train the model
model = build_model()  # Build the model
model.fit([X_train['account_number'], X_train['merchant_id'], X_train['pin_code'],
           X_train['fraud_hotspot'], X_train['amount'], X_train['rule_violation_count']],
          y_train, epochs=10, batch_size=32)

# Save the trained model for future use
model.save('fraud_detection_model_with_embeddings.h5')