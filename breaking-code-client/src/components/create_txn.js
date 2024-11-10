import React, { useState } from 'react';
import { Form, Input, Button, Select, message } from 'antd';

const { Option } = Select;

const CreateTxn = () => {
  const [form] = Form.useForm();

  const onFinish = async (values) => {
    try {
      const response = await fetch('http://13.202.202.210:8080/rulechecker', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        const data = await response.json();
        message.success('Transaction created successfully!', data);
      } else {
        message.error('Failed to create transaction');
      }
    } catch (error) {
      message.error('An error occurred: ' + error.message);
    }
  };

  return (
    <Form form={form} layout="vertical" onFinish={onFinish}>
      <Form.Item label="Account Number" name="account_number" rules={[{ required: true, message: 'Please enter your account number' }]}>
        <Input />
      </Form.Item>

      <Form.Item label="VPA" name="vpa" rules={[{ required: true, message: 'Please enter your VPA' }]}>
        <Input />
      </Form.Item>

      <Form.Item label="Origin IP" name="origin_ip" rules={[{ required: true, message: 'Please enter your origin IP' }]}>
        <Input />
      </Form.Item>

      <Form.Item label="MCC" name="mcc" rules={[{ required: true, message: 'Please enter your MCC' }]}>
        <Input />
      </Form.Item>

      <Form.Item label="Mode" name="mode" rules={[{ required: true, message: 'Please select the mode' }]}>
        <Select placeholder="Select mode">
          <Option value="UPI">UPI</Option>
          <Option value="NEFT">NEFT</Option>
          <Option value="RTGS">RTGS</Option>
        </Select>
      </Form.Item>

      <Form.Item label="Transaction ID" name="txns_id" rules={[{ required: true, message: 'Please enter the transaction ID' }]}>
        <Input type="number" />
      </Form.Item>

      <Form.Item label="Merchant ID" name="merchant_id" rules={[{ required: true, message: 'Please enter the merchant ID' }]}>
        <Input type="number" />
      </Form.Item>

      <Form.Item label="Amount" name="amount" rules={[{ required: true, message: 'Please enter the amount' }]}>
        <Input type="number" step="0.01" />
      </Form.Item>

      <Form.Item label="Narration" name="narration" rules={[{ required: true, message: 'Please enter the narration' }]}>
        <Input />
      </Form.Item>

      <Form.Item label="Device ID" name="device_id" rules={[{ required: true, message: 'Please enter the device ID' }]}>
        <Input />
      </Form.Item>

      <Form.Item label="Pin Code" name="pin_code" rules={[{ required: true, message: 'Please enter the pin code' }]}>
        <Input />
      </Form.Item>

      <Form.Item>
        <Button type="primary" htmlType="submit">
          Create Transaction
        </Button>
      </Form.Item>
    </Form>
  );
};

export {CreateTxn};
