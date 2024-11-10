import React, { useEffect, useState } from "react";
import axios from "axios";
import { Table, Pagination, Spin, Drawer, Button, Descriptions, Collapse, Tag } from "antd";
import { LoadingOutlined, EyeOutlined } from "@ant-design/icons";
import moment from "moment";
import "./FraudTransactions.css";

const { Panel } = Collapse;

const FraudTransactions = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [rulesBroken, setRulesBroken] = useState(null); // New state for rules broken
  const pageSize = 25;

  const fetchData = async (page) => {
    setLoading(true);
    try {
      const response = await axios.get(
        `http://13.202.202.210:8000/fraud_detection/api/fraud-transactions/?page=${page}`
      );
      setData(response.data.results);
      setTotalCount(response.data.count);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData(page);
  }, [page]);

  const showDrawer = (record) => {
    setSelectedRecord(record);
    setRulesBroken(record.rules_broken); // Update rules broken
    setDrawerVisible(true);
  };

  const closeDrawer = () => {
    setDrawerVisible(false);
    setSelectedRecord(null);
    setRulesBroken(null); // Reset rules broken
  };

  const parseJSONSafely = (jsonString) => {
    try {
      return JSON.parse(jsonString);
    } catch (e) {
      console.error("Error parsing JSON: ", e);
      return {};
    }
  };

  const renderTag = (label, value) => (
    <div>
      <Tag color="blue">{label}</Tag>: {JSON.stringify(value)}
    </div>
  );

  const renderApiResponse = (response) => {
    const parsedResponse = parseJSONSafely(response);
    return (
      <div>
        {parsedResponse.map((item, index) => (
          <Tag key={index} color="green">
            RuleID: {item.RuleID}, Data: {item.Data}
          </Tag>
        ))}
      </div>
    );
  };
  const columnWidth = "14.29%"; // 100% / 7 columns

  const columns = [
    { title: "Transaction ID", dataIndex: "txns_id", key: "txns_id", width: columnWidth },
    { title: "Account Number", dataIndex: "account_number", key: "account_number", width: columnWidth },
    { title: "VPA", dataIndex: "vpa", key: "vpa", width: columnWidth },
    { title: "Origin IP", dataIndex: "origin_ip", key: "origin_ip", width: columnWidth },
    { title: "Amount", dataIndex: "amount", key: "amount", width: columnWidth },
    {
      title: "ML Score",
      dataIndex: "ml_score",
      key: "ml_score",
      width: columnWidth,
      render: (text) => text !== null ? text : "N/A", // Display 'N/A' for null values
    },
    {
      title: "Action",
      key: "action",
      render: (_, record) => (
        <Button type="primary" onClick={() => showDrawer(record)}>
          <EyeOutlined />
          View Details
        </Button>
      ),
      width: columnWidth,
    },
  ];

  return (
    <div className="fraud-transactions-container">
      <h1 className="header">Fraud Transaction Data</h1>
      {loading ? (
        <Spin indicator={<LoadingOutlined style={{ fontSize: 48, color: "#6d44e5" }} spin />} />
      ) : (
        <Table
          dataSource={data}
          columns={columns}
          rowKey="txns_id"
          pagination={false}
          scroll={{ x: "max-content", y: "calc(100vh - 250px)" }}
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
        title={`Transaction Details - ${selectedRecord ? selectedRecord.txns_id : ""}`}
        visible={drawerVisible}
        onClose={closeDrawer}
        width={600}
      >
        {selectedRecord && (
          <Descriptions column={1} bordered>
            <Descriptions.Item label="Transaction ID">
              {selectedRecord.txns_id}
            </Descriptions.Item>
            <Descriptions.Item label="Account Number">
              {selectedRecord.account_number}
            </Descriptions.Item>
            <Descriptions.Item label="VPA">
              {selectedRecord.vpa}
            </Descriptions.Item>
            <Descriptions.Item label="Origin IP">
              {selectedRecord.origin_ip}
            </Descriptions.Item>
            <Descriptions.Item label="Amount">
              {selectedRecord.amount}
            </Descriptions.Item>
            <Descriptions.Item label="MCC">
              {selectedRecord.mcc}
            </Descriptions.Item>
            <Descriptions.Item label="Mode">
              {selectedRecord.mode}
            </Descriptions.Item>
            <Descriptions.Item label="Narration">
              {selectedRecord.narration}
            </Descriptions.Item>
            <Descriptions.Item label="Created Date">
              {selectedRecord.created_date
                ? moment(selectedRecord.created_date).format("YYYY-MM-DD HH:mm:ss")
                : "N/A"}
            </Descriptions.Item>
            <Descriptions.Item label="Updated Date">
              {selectedRecord.updated_date
                ? moment(selectedRecord.updated_date).format("YYYY-MM-DD HH:mm:ss")
                : "N/A"}
            </Descriptions.Item>
          </Descriptions>
        )}
        {/* Displaying Rules Broken outside of Descriptions */}
        {rulesBroken && (
          <div>
            <h3>Rules Broken</h3>
            <Collapse accordion>
              <Panel header="IP" key="1">
                {renderTag("IP", parseJSONSafely(rulesBroken.ip))}
              </Panel>
              <Panel header="Account" key="2">
                {renderTag("Account", parseJSONSafely(rulesBroken.account))}
              </Panel>
              <Panel header="Device" key="3">
                {renderTag("Device", parseJSONSafely(rulesBroken.deviceRes))}
              </Panel>
              <Panel header="Transaction Status" key="4">
                <Tag color="red">{rulesBroken.TxnsStatus}</Tag>
              </Panel>
              <Panel header="Pincode" key="5">
                {renderTag("Pincode", parseJSONSafely(rulesBroken.pincodeRes))}
              </Panel>
              <Panel header="API Response" key="6">
                {renderApiResponse(rulesBroken.api1_response)}
              </Panel>
            </Collapse>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export { FraudTransactions };
