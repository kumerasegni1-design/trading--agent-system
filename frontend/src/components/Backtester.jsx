import React, { useState } from 'react';
import { Card, Form, Input, InputNumber, Button, Select, Space, Divider, message, Table, Tag, Statistic, Row, Col } from 'antd';
import { PlayCircleOutlined, DownloadOutlined } from '@ant-design/icons';

const Backtester = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleBacktest = async (values) => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/backtesting/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values)
      });
      const data = await response.json();
      setResults(data);
      message.success('Backtest completed!');
    } catch (error) {
      console.error('Error:', error);
      message.error('Backtest failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card title="📊 Strategy Backtester" style={{ marginBottom: '24px' }}>
        <Form 
          form={form} 
          layout="vertical" 
          onFinish={handleBacktest}
        >
          <Form.Item 
            name="symbol" 
            label="Symbol" 
            initialValue="EUR/USD"
            rules={[{ required: true }]}
          >
            <Input placeholder="e.g., EUR/USD" />
          </Form.Item>

          <Form.Item 
            name="timeframe" 
            label="Timeframe" 
            initialValue="D"
            rules={[{ required: true }]}
          >
            <Select options={[
              { label: '1 Hour', value: 'H1' },
              { label: '4 Hour', value: 'H4' },
              { label: 'Daily', value: 'D' },
              { label: 'Weekly', value: 'W' }
            ]} />
          </Form.Item>

          <Form.Item 
            name="start_date" 
            label="Start Date" 
            initialValue="2021-01-01"
            rules={[{ required: true }]}
          >
            <Input type="date" />
          </Form.Item>

          <Form.Item 
            name="end_date" 
            label="End Date" 
            initialValue="2026-07-02"
            rules={[{ required: true }]}
          >
            <Input type="date" />
          </Form.Item>

          <Form.Item 
            name="initial_capital" 
            label="Initial Capital ($)" 
            initialValue={10000}
          >
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>

          <Space>
            <Button 
              type="primary" 
              icon={<PlayCircleOutlined />} 
              htmlType="submit" 
              loading={loading}
            >
              Run Backtest
            </Button>
            <Button icon={<DownloadOutlined />}>
              Export Results
            </Button>
          </Space>
        </Form>
      </Card>

      {results && (
        <Card title="📈 Backtest Results">
          <Row gutter={16} style={{ marginBottom: '24px' }}>
            <Col span={6}>
              <Statistic 
                title="Net Profit" 
                value={results.net_profit || 0} 
                prefix="$"
                valueStyle={{ color: '#52c41a' }}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="Sharpe Ratio" 
                value={results.sharpe_ratio || 0} 
                precision={2}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="Max Drawdown" 
                value={results.max_drawdown_pct || 0} 
                suffix="%"
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Col>
            <Col span={6}>
              <Statistic 
                title="Win Rate" 
                value={results.win_rate || 0} 
                suffix="%"
              />
            </Col>
          </Row>

          <Divider />

          <Table 
            columns={[
              { title: 'Metric', dataIndex: 'metric', key: 'metric' },
              { title: 'Value', dataIndex: 'value', key: 'value' }
            ]}
            dataSource={[
              { key: 1, metric: 'Total Trades', value: results.total_trades || 0 },
              { key: 2, metric: 'Winning Trades', value: results.winning_trades || 0 },
              { key: 3, metric: 'Losing Trades', value: results.losing_trades || 0 },
              { key: 4, metric: 'Profit Factor', value: (results.profit_factor || 0).toFixed(2) }
            ]}
            pagination={false}
          />
        </Card>
      )}
    </div>
  );
};

export default Backtester;
