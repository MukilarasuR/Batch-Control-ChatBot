import React, { useState } from 'react';
import { chatbotApi } from '../../services/chatbotApi';

export const TestConnection: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<string>('');
  const [query, setQuery] = useState('Where is batch VDT-052025-A?');

  const testHealthCheck = async () => {
    setIsLoading(true);
    setResult('');
    try {
      const health = await chatbotApi.healthCheck();
      setResult(`✅ Backend is healthy: ${health.service}`);
    } catch (error: any) {
      setResult(`❌ Backend connection failed: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const testChatQuery = async () => {
    setIsLoading(true);
    setResult('');
    try {
      const response = await chatbotApi.sendMessage({
        query: query,
        session_id: 'test-session'
      });
      setResult(`✅ Chat response: ${response.message}`);
    } catch (error: any) {
      setResult(`❌ Chat query failed: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h2>API Connection Test</h2>
      
      <div style={{ marginBottom: '20px' }}>
        <button 
          onClick={testHealthCheck} 
          disabled={isLoading}
          style={{ 
            padding: '10px 20px', 
            marginRight: '10px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer'
          }}
        >
          {isLoading ? 'Testing...' : 'Test Health Check'}
        </button>
        
        <button 
          onClick={testChatQuery} 
          disabled={isLoading}
          style={{ 
            padding: '10px 20px',
            backgroundColor: '#28a745',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isLoading ? 'not-allowed' : 'pointer'
          }}
        >
          {isLoading ? 'Testing...' : 'Test Chat Query'}
        </button>
      </div>

      <div style={{ marginBottom: '20px' }}>
        <label>
          Test Query:
          <input 
            type="text" 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            style={{ 
              width: '100%', 
              padding: '8px', 
              marginTop: '5px',
              border: '1px solid #ccc',
              borderRadius: '4px'
            }}
          />
        </label>
      </div>

      {result && (
        <div style={{ 
          padding: '15px', 
          backgroundColor: result.startsWith('✅') ? '#d4edda' : '#f8d7da',
          border: `1px solid ${result.startsWith('✅') ? '#c3e6cb' : '#f5c6cb'}`,
          borderRadius: '4px',
          whiteSpace: 'pre-wrap'
        }}>
          {result}
        </div>
      )}
    </div>
  );
};