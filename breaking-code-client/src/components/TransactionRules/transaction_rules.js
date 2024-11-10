import React, { useEffect, useState } from "react";
import axios from "axios";
import { Table, Pagination, Spin, Drawer, Button, Descriptions } from "antd";
import { LoadingOutlined, EyeOutlined } from "@ant-design/icons";
import moment from "moment"; // Import moment
import "./TransactionRules.css"; // Import your CSS file

const TransactionRules = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [selectedRule, setSelectedRule] = useState(null); // For holding the selected row details
  const pageSize = 25; // Number of items per page

  const fetchData = async (page) => {
    setLoading(true);
    try {
      const response = await axios.get(
        `http://13.202.202.210:8000/fraud_detection/api/transaction-rules/?page=${page}`
      );
      setData(response.data.results); // Use 'results' array
      setTotalCount(response.data.count); // Total count of items
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(page);
  }, [page]);

  const openDrawer = (record) => {
    setSelectedRule(record); // Set the selected row data to show in the drawer
    setDrawerVisible(true); // Open the drawer
  };

  const closeDrawer = () => {
    setDrawerVisible(false); // Close the drawer
    setSelectedRule(null); // Clear selected rule data
  };

  const columns = [
    {
      title: "Rule ID",
      dataIndex: "rule_id",
      key: "rule_id",
      width: 100,
    },
    {
      title: "Rule Title",
      dataIndex: "rule_title",
      key: "rule_title",
      width: 200,
    },
    {
      title: "Fraud Entity",
      dataIndex: "fraud_entity",
      key: "fraud_entity",
      width: 150,
    },
    {
      title: "Fraud Type",
      dataIndex: "fraud_type",
      key: "fraud_type",
      width: 150,
    },
    {
      title: "Rule Score",
      dataIndex: "rule_score",
      key: "rule_score",
      width: 100,
    },
    {
      title: "Description",
      dataIndex: "rule_description",
      key: "rule_description",
      width: 250,
    },
    {
      title: "Created Date",
      dataIndex: "created_date",
      key: "created_date",
      width: 180,
      render: (text) => moment(text).format("YYYY-MM-DD HH:mm:ss"), // Format date using moment
    },
    {
      title: "Updated Date",
      dataIndex: "updated_date",
      key: "updated_date",
      width: 180,
      render: (text) => moment(text).format("YYYY-MM-DD HH:mm:ss"), // Format date using moment
    },
    {
      title: "Action",
      key: "action",
      width: 150,
      render: (_, record) => (
        <Button type="primary" onClick={() => openDrawer(record)}>
          <EyeOutlined />View Details
        </Button>
      ),
    },
  ];

  return (
    <div className="fraud-transactions-container">
      <h1 className="header">Transaction Rules</h1>
      {loading ? (
        <Spin
          indicator={
            <LoadingOutlined style={{ fontSize: 48, color: "#6d44e5" }} spin />
          }
        />
      ) : (
        <Table
          dataSource={data}
          columns={columns}
          rowKey="rule_id"
          pagination={false}
          scroll={{ x: "max-content", y: "calc(100vh - 250px)" }} // Adjust vertical height as needed
          className="fraud-table"
        />
      )}
      <Pagination
        current={page}
        pageSize={pageSize}
        total={totalCount}
        onChange={(page) => setPage(page)}
        showSizeChanger={false}
        className="pagination"
      />
      <Drawer
        title={`Rule Details - ${selectedRule ? selectedRule.rule_title : ""}`}
        width={600}
        onClose={closeDrawer}
        visible={drawerVisible}
        placement="right"
      >
        {selectedRule && (
          <div>
            <Descriptions column={1} bordered>
              <Descriptions.Item label="Rule ID">
                {selectedRule.rule_id}
              </Descriptions.Item>
              <Descriptions.Item label="Rule Title">
                {selectedRule.rule_title}
              </Descriptions.Item>
              <Descriptions.Item label="Fraud Entity">
                {selectedRule.fraud_entity}
              </Descriptions.Item>
              <Descriptions.Item label="Fraud Type">
                {selectedRule.fraud_type}
              </Descriptions.Item>
              <Descriptions.Item label="Rule Score">
                {selectedRule.rule_score}
              </Descriptions.Item>
              <Descriptions.Item label="Description">
                {selectedRule.rule_description}
              </Descriptions.Item>
              <Descriptions.Item label="Created Date">
                {moment(selectedRule.created_date).format(
                  "YYYY-MM-DD HH:mm:ss"
                )}
              </Descriptions.Item>
              <Descriptions.Item label="Updated Date">
                {moment(selectedRule.updated_date).format(
                  "YYYY-MM-DD HH:mm:ss"
                )}
              </Descriptions.Item>
            </Descriptions>

            {/* SQL Query displayed separately without Descriptions */}
            <div style={{ marginTop: "20px" }}>
              <h3>SQL Query</h3>
              <pre style={{ whiteSpace: "pre-wrap" }}>
                {selectedRule.sql_query}
              </pre>{" "}
              {/* SQL query in preformatted text */}
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export { TransactionRules };
