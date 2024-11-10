# Fraud Transaction Monitor

**Project developed for:** 𝐅𝐢𝐧𝐇𝐢𝐯𝐞'𝟐𝟒 Hackathon  
**Team Name:** Breaking Code

## Overview

The **Fraud Transaction Monitor** is a full-stack project developed during the 𝐅𝐢𝐧𝐇𝐢𝐯𝐞'𝟐𝟒 Hackathon to monitor and detect fraudulent transactions in real-time. This solution leverages Django for the backend, React for the frontend, Druid for real-time analytics, and TensorFlow for machine learning, with the goal of identifying suspicious transactions quickly and accurately. The system applies rule-based logic and machine learning predictions to detect fraud, following guidelines provided by the Indian Financial Intelligence Unit (FIU).

My primary contribution to this project was designing and implementing the machine learning model responsible for real-time fraud detection.

## Use Case: Transaction Fraud Monitoring

This system addresses the need for real-time monitoring of financial transactions to prevent fraud. Transactions are flagged based on:

- **Negative Lists**: Elements like flagged account numbers, IP addresses, pin codes, and device IDs are temporarily or permanently blocked.
- **Transaction Velocity**: Detects abnormal transaction frequency from a single merchant or account.
  - _Example_: A merchant should not process more than 20 transactions in 10 seconds.
- **Gross Merchandise Value (GMV)**: Flags merchants processing unusually high transaction values over short periods.
  - _Example_: A merchant should not handle transactions totaling more than Rs 200,000 in 10 seconds.

The system accepts transaction data in JSON format and flags any transaction that violates the rules, providing real-time insights for fraud detection.

## Features

- **Real-Time Fraud Detection**: Identifies fraudulent transactions instantly based on rules and ML predictions.
- **Customizable Rules**: Allows administrators to define transaction limits and thresholds for multiple merchants.
- **Efficient Data Handling**: Built to manage high transaction volumes while minimizing false positives.
- **API-Driven**: RESTful endpoints support integration with external services, allowing data input via HTTP API, Kafka, or SQS.

## Tech Stack

- **Backend**: Python (Django), Golang
- **Frontend**: React.js
- **Real-Time Analytics**: Druid
- **Messaging**: Kafka
- **Machine Learning**: TensorFlow with embedding layers for high-cardinality categorical data
- **Database**: PostgreSQL

## Machine Learning Model

As part of the fraud detection system, I developed a machine learning model in TensorFlow with the following specifics:

1. **Model Architecture**:
   - **Embedding Layers**: Used embedding layers to handle high-cardinality categorical features, such as `account_number`, `merchant_id`, and `pin_code`. This allows the model to capture patterns in high-dimensional categorical data effectively, which is crucial in fraud detection.
   - **Dense Layers**: Added dense layers with ReLU activation to learn relationships in the transaction data and output fraud likelihood scores.
   - **Sigmoid Output Layer**: Used a sigmoid activation function in the output layer for binary classification, predicting fraud probabilities for each transaction.

2. **Feature Engineering**:
   - **High-Value Flag**: Transactions above a certain value were flagged as high-value, aiding the model in detecting potential fraud.
   - **Fraud Hotspot Detection**: Transactions from known fraud-prone locations were marked, providing context for location-based fraud.
   - **Rule Violation Count**: Tracked the number of rule violations per transaction, helping the model learn from patterns in transactional behavior.

3. **Data Handling**:
   - **Real-Time Kafka Streaming**: Integrated Kafka for ingesting and processing real-time transaction data, allowing the model to make timely predictions.
   - **PostgreSQL Integration**: The model outputs fraud scores directly into PostgreSQL for further monitoring and analysis.

4. **Training Process**:
   - The model was trained on historical transaction data, with custom preprocessing steps for categorical encoding and standardization of numerical features.
   - Achieved high accuracy by combining the embedding-based ML model with rule-based thresholds, reducing false positives and enhancing fraud detection precision.

## Architecture
![Screenshot from 2024-11-10 23-53-44](https://github.com/user-attachments/assets/44aacd28-20f7-452c-816f-b88686df98dd)



The architecture integrates rule-based detection with ML predictions, using Kafka for streaming and Druid for high-speed analytics. Embedding layers in the ML model allow efficient handling of high-cardinality fields like account numbers and merchant IDs, crucial for identifying fraud patterns.

## Usage

Access the application via the frontend to set up monitoring rules and view transaction data flagged as potentially fraudulent.

## Model Training and Real-Time Fraud Detection

### `train_final_model.py`

This script builds and trains the fraud detection model using TensorFlow. Key steps:
- **Data Preprocessing**: Flags high-value transactions, counts rule violations, and identifies fraud-prone areas.
- **Model Architecture**: Embedding layers handle high-cardinality features, and dense layers process the data for fraud classification.
- **Real-Time Data Collection**: Uses Kafka to ingest real-time transaction data for training.

### `get_results.py`

This script is responsible for deploying the trained model in real-time:
- **Data Preprocessing**: Similar to the training script, with Kafka ingesting transactions to flag fraud.
- **Real-Time Prediction**: The model predicts fraud likelihood and updates scores in PostgreSQL for monitoring.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
