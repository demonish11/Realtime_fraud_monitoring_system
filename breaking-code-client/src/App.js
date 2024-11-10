import React, { useState } from "react";
import { Layout, Menu } from "antd";
import {
  AppstoreOutlined,
  TransactionOutlined,
  ToolOutlined,
  OrderedListOutlined,
} from "@ant-design/icons";
import {
  CreateTxn,
  FraudTransactions,
  RuleBreaker,
  TransactionRules,
} from "./components";

const { Header, Content, Footer, Sider } = Layout;

const App = () => {
  const [selectedApp, setSelectedApp] = useState("fraud");

  const renderSelectedApp = () => {
    switch (selectedApp) {
      case "fraud":
        return <FraudTransactions />;
      case "create":
        return <CreateTxn />;
      case "rule_list":
        return <TransactionRules />;
      case "rule_breaker":
        return <RuleBreaker />;
      default:
        return <div>Select an app to start</div>;
    }
  };

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider
        collapsible
        style={{
          position: "fixed",
          height: "100vh",
          left: 0,
          top: 0,
          bottom: 0,
        }}
      >
        <div
          className="logo"
          style={{ color: "white", fontSize: 20, padding: 10 }}
        >
          Navigation
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedApp]}
          onClick={(e) => setSelectedApp(e.key)}
        >
          <Menu.Item key="fraud" icon={<TransactionOutlined />}>
            Transaction Fraud Monitoring
          </Menu.Item>
          <Menu.Item key="rule_breaker" icon={<ToolOutlined />}>
            Rule Creator
          </Menu.Item>
          <Menu.Item key="rule_list" icon={<OrderedListOutlined />}>
            Rules List
          </Menu.Item>
          <Menu.Item key="create" icon={<AppstoreOutlined />}>
            Create Transaction
          </Menu.Item>
        </Menu>
      </Sider>
      <Layout style={{ marginLeft: 200 }}>
        {" "}
        {/* Offset the content to accommodate the fixed sidebar */}
        <Header
          style={{
            padding: 0,
            backgroundColor: "#001529",
            textAlign: "center",
            color: "#fff",
          }}
        >
          <h1>Fraud Transaction Management System</h1>
        </Header>
        <Content
          style={{
            margin: "24px 16px 0",
            padding: 24,
            backgroundColor: "#fff",
            overflow: "auto",
          }}
        >
          {renderSelectedApp()}
        </Content>
        <Footer style={{ textAlign: "center" }}>Breaking Code ©2024</Footer>
      </Layout>
    </Layout>
  );
};

export default App;
