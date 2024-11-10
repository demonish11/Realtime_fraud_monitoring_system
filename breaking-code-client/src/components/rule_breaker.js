import React, { useState } from "react";
import { Form, Input, Button, Card, Select, Space, message } from "antd";
import { MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";
import axios from "axios";

const { Option } = Select;

// Allowed fields for the dropdown
const allowedFields = [
  'TIMESTAMP_TO_MILLIS("__time")', // New Field Added
  "account_number",
  "vpa",
  "origin_ip",
  "mcc",
  "mode",
  "txns_id",
  "merchant_id",
  "amount",
  "narration",
  "device_id",
  "pin_code",
];

// Extend the operator list to include <= and >=
const operatorOptions = [
  { value: "=", label: "=" },
  { value: ">", label: ">" },
  { value: "<", label: "<" },
  { value: ">=", label: ">=" }, // New operator
  { value: "<=", label: "<=" }, // New operator
  { value: "IN", label: "IN" },
];

// Fraud Entity options
const fraudEntityOptions = [
  { value: "merchant", label: "Merchant" },
  { value: "customer", label: "Customer" },
  // Add more entities as needed
];

// Fraud Type options (same as in the model)
const fraudTypeOptions = [
  { value: "TRANSACTION_VELOCITY", label: "Transaction Velocity" },
  { value: "NEGATIVE_LIST", label: "Negative List" },
  { value: "GMV_LIMIT_EXCEEDED", label: "GMV Limit Exceeded" },
  { value: "SUSPICIOUS_IP", label: "Suspicious IP Address" },
  { value: "DEVICE_FRAUD", label: "Device Fraud" },
  { value: "CARD_FRAUD", label: "Card Fraud" },
  { value: "MULTIPLE_TXNS", label: "Multiple Transactions in Short Time" },
];

const RuleBreaker = () => {
  const [generatedSQL, setGeneratedSQL] = useState("");
  const [loading, setLoading] = useState(false);
  const [ruleScore, setRuleScore] = useState(0);
  const [ruleDescription, setRuleDescription] = useState("");
  const [ruleTitle, setRuleTitle] = useState("");
  const [merchantId, setMerchantId] = useState("");
  const [fraudEntity, setFraudEntity] = useState("");
  const [fraudType, setFraudType] = useState("");
  const [selectClause, setSelectClause] = useState(""); // New state for select_clause

  const onFinish = async (values) => {
    const groupConditions = values.groups.map((group) => ({
      logic: group.logic,
      conditions: group.conditions.map((condition) => ({
        field: condition.field,
        operator: condition.operator,
        value: condition.value,
      })),
    }));

    const requestData = {
      condition: {
        logic: values.logic,
        conditions: groupConditions,
      },
      table_name: "transactions",
      fraud_entity: fraudEntity, // Add Fraud Entity to request data
      fraud_type: fraudType, // Add Fraud Type to request data
      select_clause: selectClause || "*", // Default to '*' if nothing is entered
    };

    setLoading(true);
    try {
      const response = await axios.post(
        "http://13.202.202.210:8000/fraud_detection/api/generate-sql/",
        requestData
      );
      const sqlQuery = response.data.sql_query;
      setGeneratedSQL(sqlQuery);
      message.success("SQL query generated successfully!");
    } catch (error) {
      message.error("Error generating SQL query.");
    } finally {
      setLoading(false);
    }
  };

  const submitSQL = async () => {
    if (!generatedSQL) {
      message.error("No SQL query to submit.");
      return;
    }

    try {
      await axios.post(
        "http://13.202.202.210:8000/fraud_detection/api/submit-rule/",
        {
          sql_query: generatedSQL,
          rule_score: ruleScore,
          rule_description: ruleDescription,
          rule_title: ruleTitle,
          merchant_id: merchantId || "all", // Set to 'all' if merchantId is not provided
          fraud_entity: fraudEntity, // Include Fraud Entity in submission
          fraud_type: fraudType, // Include Fraud Type in submission
        }
      );
      message.success("SQL query and rule submitted successfully!");
    } catch (error) {
      message.error("Error submitting SQL query and rule.");
    }
  };

  return (
    <Card
      title="SQL Query Generator"
      bordered={true}
      style={{ width: 800, margin: "50px auto" }}
    >
      <Form
        layout="vertical"
        onFinish={onFinish}
        initialValues={{ logic: "AND" }}
      >
        <Form.Item
          label="Outer Logic"
          name="logic"
          rules={[{ required: true, message: "Please select logic (AND/OR)!" }]}
        >
          <Select>
            <Option value="AND">AND</Option>
            <Option value="OR">OR</Option>
          </Select>
        </Form.Item>

        {/* Rest of the form (Condition Groups) */}
        <Form.List name="groups">
          {(fields, { add, remove }) => (
            <>
              {fields.map(({ key, name, fieldKey, ...restField }) => (
                <Card
                  key={key}
                  title={`Condition Group ${key + 1}`}
                  style={{ marginBottom: 16 }}
                >
                  <Form.Item
                    {...restField}
                    name={[name, "logic"]}
                    fieldKey={[fieldKey, "logic"]}
                    rules={[
                      {
                        required: true,
                        message: "Please select group logic (AND/OR)!",
                      },
                    ]}
                    label="Group Logic"
                  >
                    <Select>
                      <Option value="AND">AND</Option>
                      <Option value="OR">OR</Option>
                    </Select>
                  </Form.Item>

                  <Form.List name={[name, "conditions"]}>
                    {(
                      conditionFields,
                      { add: addCondition, remove: removeCondition }
                    ) => (
                      <>
                        {conditionFields.map(
                          ({
                            key: condKey,
                            name: condName,
                            fieldKey: condFieldKey,
                            ...restCondField
                          }) => (
                            <Space
                              key={condKey}
                              style={{ display: "flex", marginBottom: 8 }}
                              align="baseline"
                            >
                              <Form.Item
                                {...restCondField}
                                name={[condName, "field"]}
                                fieldKey={[condFieldKey, "field"]}
                                rules={[
                                  {
                                    required: true,
                                    message: "Please select a field!",
                                  },
                                ]}
                              >
                                <Select placeholder="Select Field">
                                  {allowedFields.map((field) => (
                                    <Option key={field} value={field}>
                                      {field}
                                    </Option>
                                  ))}
                                </Select>
                              </Form.Item>

                              <Form.Item
                                {...restCondField}
                                name={[condName, "operator"]}
                                fieldKey={[condFieldKey, "operator"]}
                                rules={[
                                  {
                                    required: true,
                                    message: "Please select operator!",
                                  },
                                ]}
                              >
                                <Select placeholder="Operator">
                                  {operatorOptions.map((operator) => (
                                    <Option
                                      key={operator.value}
                                      value={operator.value}
                                    >
                                      {operator.label}
                                    </Option>
                                  ))}
                                </Select>
                              </Form.Item>

                              <Form.Item
                                {...restCondField}
                                name={[condName, "value"]}
                                fieldKey={[condFieldKey, "value"]}
                                rules={[
                                  {
                                    required: true,
                                    message: "Please input the value!",
                                  },
                                ]}
                              >
                                <Input placeholder="Value" />
                              </Form.Item>

                              <MinusCircleOutlined
                                onClick={() => removeCondition(condName)}
                              />
                            </Space>
                          )
                        )}
                        <Form.Item>
                          <Button
                            type="dashed"
                            onClick={() => addCondition()}
                            block
                            icon={<PlusOutlined />}
                          >
                            Add Condition
                          </Button>
                        </Form.Item>
                      </>
                    )}
                  </Form.List>

                  <Button type="danger" onClick={() => remove(name)} block>
                    Remove Group
                  </Button>
                </Card>
              ))}
              <Form.Item>
                <Button
                  type="dashed"
                  onClick={() => add()}
                  block
                  icon={<PlusOutlined />}
                >
                  Add Condition Group
                </Button>
              </Form.Item>
            </>
          )}
        </Form.List>

        {/* Select Clause Input */}
        <Form.Item label="SELECT Clause">
          <Input
            value={selectClause}
            onChange={(e) => setSelectClause(e.target.value)}
            placeholder="e.g., SUM(amount)"
          />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit" loading={loading} block>
            Generate SQL Query
          </Button>
        </Form.Item>
      </Form>

      {generatedSQL && (
        <Card title="Generated SQL" bordered={true} style={{ marginTop: 16 }}>
          <pre>{generatedSQL}</pre>
          <Form layout="vertical">
            {/* Fraud Entity Selection */}
            <Form.Item label="Fraud Entity">
              <Select
                placeholder="Select Fraud Entity"
                value={fraudEntity}
                onChange={setFraudEntity}
              >
                {fraudEntityOptions.map((entity) => (
                  <Option key={entity.value} value={entity.value}>
                    {entity.label}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            {/* Fraud Type Selection */}
            <Form.Item label="Fraud Type">
              <Select
                placeholder="Select Fraud Type"
                value={fraudType}
                onChange={setFraudType}
              >
                {fraudTypeOptions.map((type) => (
                  <Option key={type.value} value={type.value}>
                    {type.label}
                  </Option>
                ))}
              </Select>
            </Form.Item>

            <Form.Item label="Rule Score">
              <Input
                value={ruleScore}
                onChange={(e) => setRuleScore(e.target.value)}
                placeholder="Enter rule score"
              />
            </Form.Item>
            <Form.Item label="Rule Title">
              <Input
                value={ruleTitle}
                onChange={(e) => setRuleTitle(e.target.value)}
                placeholder="Enter rule title"
              />
            </Form.Item>
            <Form.Item label="Rule Description">
              <Input
                value={ruleDescription}
                onChange={(e) => setRuleDescription(e.target.value)}
                placeholder="Enter rule description"
              />
            </Form.Item>
            <Form.Item label="Merchant ID">
              <Input
                value={merchantId}
                onChange={(e) => setMerchantId(e.target.value)}
                placeholder="Enter merchant ID (optional)"
              />
            </Form.Item>
            <Button type="primary" onClick={submitSQL} block>
              Submit SQL Query and Rule
            </Button>
          </Form>
        </Card>
      )}
    </Card>
  );
};

export { RuleBreaker };
