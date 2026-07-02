import React, { useState, useRef } from 'react';
import { Input, Button, Card, Space, Tag, Spin, message, Divider } from 'antd';
import { SendOutlined, ClearOutlined } from '@ant-design/icons';
import './CommandCenter.css';

const CommandCenter = () => {
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'system',
      text: '👋 Welcome to Trading Agent Command Center! Send me a prompt to start building trading strategies.'
    }
  ]);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  React.useEffect(scrollToBottom, [messages]);

  const handleSendCommand = async () => {
    if (!prompt.trim()) return;

    // Add user message
    setMessages(prev => [...prev, {
      id: prev.length + 1,
      type: 'user',
      text: prompt
    }]);

    setLoading(true);
    setPrompt('');

    try {
      const response = await fetch('http://localhost:8000/ws/command', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });

      const data = await response.json();
      
      // Add system response
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        type: 'system',
        text: `✅ Task ID: ${data.task_id}\nStatus: ${data.status}\nMessage: ${data.message}`
      }]);

      message.success('Command dispatched to agents!');
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        type: 'error',
        text: `❌ Error: ${error.message}`
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="🎤 Command Center - Dispatch Agents" style={{ height: '600px', display: 'flex', flexDirection: 'column' }}>
      <div style={{ flex: 1, overflowY: 'auto', marginBottom: '16px', padding: '12px', border: '1px solid #d9d9d9', borderRadius: '4px', backgroundColor: '#fafafa' }}>
        {messages.map(msg => (
          <div key={msg.id} style={{ marginBottom: '12px' }}>
            {msg.type === 'user' && (
              <div style={{ textAlign: 'right' }}>
                <Tag color="blue" style={{ maxWidth: '70%', display: 'inline-block', textAlign: 'left' }}>
                  {msg.text}
                </Tag>
              </div>
            )}
            {msg.type === 'system' && (
              <div style={{ textAlign: 'left' }}>
                <Tag color="green" style={{ maxWidth: '70%', display: 'inline-block', textAlign: 'left', whiteSpace: 'pre-wrap' }}>
                  {msg.text}
                </Tag>
              </div>
            )}
            {msg.type === 'error' && (
              <div style={{ textAlign: 'left' }}>
                <Tag color="red" style={{ maxWidth: '70%', display: 'inline-block', textAlign: 'left' }}>
                  {msg.text}
                </Tag>
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <Divider style={{ margin: '8px 0' }} />
      
      <Space style={{ width: '100%' }} direction="vertical">
        <Input.TextArea
          placeholder="Enter your command here... (e.g., 'Generate a mean reversion strategy on EUR/USD')"
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          rows={3}
          onPressEnter={e => {
            if (e.ctrlKey || e.metaKey) handleSendCommand();
          }}
        />
        <Space style={{ width: '100%', justifyContent: 'flex-end' }}>
          <Button 
            type="primary" 
            icon={<SendOutlined />} 
            onClick={handleSendCommand}
            loading={loading}
            disabled={!prompt.trim()}
          >
            Send Command
          </Button>
          <Button 
            icon={<ClearOutlined />} 
            onClick={() => {
              setMessages([{ id: 1, type: 'system', text: '🔄 Chat cleared' }]);
              setPrompt('');
            }}
          >
            Clear
          </Button>
        </Space>
      </Space>
    </Card>
  );
};

export default CommandCenter;
