import React, { useState, useEffect } from 'react';
import { Table, Card, Tag, Space, Button, Statistic, Row, Col, Progress } from 'antd';
import { ReloadOutlined, CheckCircleOutlined, ClockCircleOutlined } from '@ant-design/icons';

const AgentMonitor = ({ agents = [] }) => {
  const [agentData, setAgentData] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchAgents = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/agents/status');
      const data = await response.json();
      setAgentData(data.agents || []);
    } catch (error) {
      console.error('Error fetching agents:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAgents();
    const interval = setInterval(fetchAgents, 5000); // Refresh every 5s
    return () => clearInterval(interval);
  }, []);

  const columns = [
    {
      title: 'Agent Name',
      dataIndex: 'name',
      key: 'name',
      render: (text) => <strong>{text}</strong>
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={status === 'active' ? 'green' : 'red'}>
          {status === 'active' ? '✅ Active' : '❌ Inactive'}
        </Tag>
      )
    },
    {
      title: 'Tasks Completed',
      dataIndex: 'tasks_completed',
      key: 'tasks_completed',
      render: (num) => <strong>{num}</strong>
    },
    {
      title: 'CPU Usage',
      dataIndex: 'cpu',
      key: 'cpu',
      render: (percent = 0) => <Progress percent={percent} size="small" />
    }
  ];

  return (
    <Card title="🤖 Agent Monitor" extra={<Button icon={<ReloadOutlined />} onClick={fetchAgents} loading={loading} />}>
      <Row gutter={16} style={{ marginBottom: '24px' }}>
        <Col span={6}>
          <Statistic title="Total Agents" value={agentData.length} prefix="🤖" />
        </Col>
        <Col span={6}>
          <Statistic 
            title="Active" 
            value={agentData.filter(a => a.status === 'active').length} 
            valueStyle={{ color: '#52c41a' }}
            prefix="✅"
          />
        </Col>
        <Col span={6}>
          <Statistic 
            title="Total Tasks" 
            value={agentData.reduce((sum, a) => sum + (a.tasks_completed || 0), 0)}
            prefix="✔️"
          />
        </Col>
        <Col span={6}>
          <Statistic title="Last Updated" value={new Date().toLocaleTimeString()} />
        </Col>
      </Row>
      
      <Table 
        columns={columns} 
        dataSource={agentData.map((a, i) => ({ ...a, key: i }))} 
        loading={loading}
        pagination={false}
      />
    </Card>
  );
};

export default AgentMonitor;
