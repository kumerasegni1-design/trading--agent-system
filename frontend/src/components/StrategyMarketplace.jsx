import React, { useState, useEffect } from 'react';
import { Card, Table, Button, Tag, Space, Row, Col, Statistic, Input } from 'antd';
import { ShoppingCartOutlined, DeploymentUnitOutlined } from '@ant-design/icons';

const StrategyMarketplace = () => {
  const [strategies, setStrategies] = useState([]);
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchMarketplace();
  }, []);

  const fetchMarketplace = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/marketplace/stats');
      const data = await response.json();
      // In real app, fetch actual lists
      setStrategies(data.strategies || []);
      setModels(data.models || []);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const strategyColumns = [
    { title: 'Strategy Name', dataIndex: 'name', key: 'name' },
    { title: 'Type', dataIndex: 'type', key: 'type' },
    { 
      title: 'Status', 
      dataIndex: 'status', 
      key: 'status',
      render: (status) => <Tag color={status === 'live' ? 'green' : 'blue'}>{status}</Tag>
    },
    { title: 'PnL', dataIndex: 'pnl', key: 'pnl', render: (pnl) => <strong>${pnl}</strong> },
    {
      title: 'Actions',
      key: 'actions',
      render: () => (
        <Space>
          <Button size="small">View</Button>
          <Button size="small" type="primary">Deploy</Button>
        </Space>
      )
    }
  ];

  const modelColumns = [
    { title: 'Model Name', dataIndex: 'name', key: 'name' },
    { title: 'Algorithm', dataIndex: 'algorithm', key: 'algorithm' },
    { title: 'Accuracy', dataIndex: 'accuracy', key: 'accuracy', render: (acc) => `${acc}%` },
    { 
      title: 'Status', 
      dataIndex: 'status', 
      key: 'status',
      render: (status) => <Tag color={status === 'live' ? 'green' : 'processing'}>{status}</Tag>
    },
    {
      title: 'Actions',
      key: 'actions',
      render: () => (
        <Space>
          <Button size="small">Test</Button>
          <Button size="small" type="primary" icon={<DeploymentUnitOutlined />}>Deploy</Button>
        </Space>
      )
    }
  ];

  return (
    <div>
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={16}>
          <Col span={8}>
            <Statistic title="Total Strategies" value={strategies.length} prefix="📈" />
          </Col>
          <Col span={8}>
            <Statistic title="Deployed Models" value={models.length} prefix="🎯" />
          </Col>
          <Col span={8}>
            <Statistic title="Total PnL" value="$1,250.50" prefix="💰" valueStyle={{ color: '#52c41a' }} />
          </Col>
        </Row>
      </Card>

      <Card title="📈 Strategies" style={{ marginBottom: '24px' }}>
        <Space style={{ marginBottom: '16px', width: '100%', justifyContent: 'space-between' }}>
          <Input.Search 
            placeholder="Search strategies..."
            style={{ width: '300px' }}
            onChange={e => setSearchTerm(e.target.value)}
          />
          <Button type="primary" icon={<ShoppingCartOutlined />}>Browse All</Button>
        </Space>
        <Table columns={strategyColumns} dataSource={strategies} loading={loading} pagination={false} />
      </Card>

      <Card title="🎯 ML Models">
        <Table columns={modelColumns} dataSource={models} loading={loading} pagination={false} />
      </Card>
    </div>
  );
};

export default StrategyMarketplace;
