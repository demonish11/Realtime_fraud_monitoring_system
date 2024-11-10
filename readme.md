# Breaking Code - Transaction Fraud Monitor

**Project developed for:** 𝐅𝐢𝐧𝐇𝐢𝐯𝐞'𝟐𝟒 Hackathon  
**Team Name:** Breaking Code

## Overview

Breaking Code is a full-stack project developed during the 𝐅𝐢𝐧𝐇𝐢𝐯𝐞'𝟐𝟒 Hackathon to monitor and detect fraudulent transactions in real-time. This solution leverages Django for the backend, React for the frontend, Druid for real-time analytics, and TensorFlow for machine learning, with the goal of identifying suspicious transactions quickly and accurately. The system applies rule-based logic and machine learning predictions to detect fraud, following guidelines provided by the Indian Financial Intelligence Unit (FIU).

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

## Architecture


The architecture integrates rule-based detection with ML predictions, using Kafka for streaming and Druid for high-speed analytics. Embedding layers in the ML model allow efficient handling of high-cardinality fields like account numbers and merchant IDs, crucial for identifying fraud patterns.

## Installation

### 1. Clone the Repository

```bash
git clone https://bitbucket.org/easebuzz1/breaking-code/src/main/
cd breaking-code

