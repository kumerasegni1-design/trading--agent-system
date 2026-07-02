import React, { useState, useEffect } from 'react';
import { Layout, Menu, Breadcrumb, Button, Input, Space, Row, Col, Card, Statistic, Tabs, Table, Tag, Progress } from 'antd';
import { SendOutlined, ReloadOutlined, DatabaseOutlined, RocketOutlined } from '@ant-design/icons';
import CommandCenter from './components/CommandCenter';
import AgentMonitor from './components/AgentMonitor';
import StrategyMarketplace from './components/StrategyMarketplace';
import Backtester from './components/Backtester';
import './App.css';

const { Header, Content, Sider } = Layout;

function App() {
  const [currentTab, setCurrentTab] = useState('command');
  const [wsConnected, setWsConnected] = useState(false);
  const [agents, setAgents] = useState([]);
  const [strategies, setStrategies] = useState([]);
  const [models, setModels] = useState([]);

  useEffect(() => {
    // Connect to WebSocket
    const ws = new WebSocket('ws://localhost:8000/ws/command');
    
    ws.onopen = () => {
      console.log('✅ WebSocket connected');
      setWsConnected(true);
      fetchAgentStatus();
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('📨 Message received:', data);
      // Handle incoming messages
    };
    
    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
      setWsConnected(false);
    };
    
    return () => ws.close();
  }, []);

  const fetchAgentStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/agents/status');
      const data = await response.json();
      setAgents(Object.values(data));
    } catch (error) {
      console.error('Error fetching agent status:', error);
    }
  };

  const tabItems = [
    {
      key: 'command',
      label: '🎤 Command Center',
      children: <CommandCenter />
    },
    {
      key: 'agents',
      label: '🤖 Agent Monitor',
      children: <AgentMonitor agents={agents} />
    },
    {
      key: 'backtesting',
      label: '📊 Backtesting',
      children: <Backtester />
    },
    {
      key: 'marketplace',
      label: '🛒 Marketplace',
      children: <StrategyMarketplace />
    }
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h1 style={{ color: 'white', margin: 0 }}>🤖 Trading Agent System</h1>
        <div style={{ color: wsConnected ? '#52c41a' : '#ff4d4f' }}>
          {wsConnected ? '✅ Connected' : '❌ Disconnected'}
        </div>
      </Header>
      
      <Layout>
        <Content style={{ margin: '24px 16px' }}>
          <Card style={{ marginBottom: '24px' }}>
            <Row gutter={16}>
              <Col span={6}>
                <Statistic title="Active Agents" value={agents.length} prefix="🤖" />
              </Col>
              <Col span={6}>
                <Statistic title="Strategies" value={strategies.length} prefix="📈" />
              </Col>
              <Col span={6}>
                <Statistic title="Deployed Models" value={models.length} prefix="🎯" />
              </Col>
              <Col span={6}>
                <Statistic title="System Status" value="Online" valueStyle={{ color: '#52c41a' }} />
              </Col>
            </Row>
          </Card>

          <Card>
            <Tabs items={tabItems} onChange={setCurrentTab} />
          </Card>
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
