import React, { useState, useRef, useEffect } from 'react';
import { Send, User, Bot } from 'lucide-react';
import './App.css';

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: object | string;
  timestamp: Date;
};

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: `${Date.now()}`,
      role: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputValue }) // 🔁 key must match FastAPI model
      });

      const data = await response.json();
      const botMessage: Message = {
        id: `${Date.now()}`,
        role: 'assistant',
        content: data.response, // 🔁 must use response field
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chatbot error:', error);
      setMessages(prev => [
        ...prev,
        {
          id: `${Date.now()}`,
          role: 'assistant',
          content: '⚠️ Failed to process your request. Try again.',
          timestamp: new Date()
        }
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="container">
      <div className="chat-header">
        <div className="chat-header-content">
          <div className="chat-header-avatar">
            <Bot size={20} color="white" />
          </div>
          <div>
            <h1 className="chat-header-title">AI Assistant</h1>
            <p className="chat-header-subtitle">Online</p>
          </div>
        </div>
      </div>

      <div className="chat-messages-container">
        <div className="chat-messages-wrapper">
          {messages.map(renderMessage)}
          {isTyping && (
            <div className="typing-container">
              <div className="typing-wrapper">
                <div className="bot-avatar">
                  <Bot size={16} color="white" />
                </div>
                <div className="typing-bubble">
                  <div className="typing-dots">
                    <div className="typing-dot typing-dot-1" />
                    <div className="typing-dot typing-dot-2" />
                    <div className="typing-dot" />
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <div className="chat-input-container">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your message..."
            className="chat-textarea"
            rows={2}
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim()}
            className="chat-send-button"
          >
            <Send size={16} color="white" />
          </button>
        </div>
      </div>
    </div>
  );
};

const renderMessage = (message: Message) => {
  if (message.role === 'user' && typeof message.content === 'string') {
    return (
      <div key={message.id} className="user-message-container">
        <div className="user-message-wrapper">
          <div className="user-message-bubble">
            <p className="message-text">{message.content}</p>
          </div>
          <div className="user-avatar">
            <User size={16} color="white" />
          </div>
        </div>
      </div>
    );
  } else {
    const content = message.content;
    const isTable = typeof content === 'string' && content.includes('|') && content.includes('\n');

    return (
      <div key={message.id} className="bot-message-container">
        <div className="bot-message-wrapper">
          <div className="bot-avatar">
            <Bot size={16} color="white" />
          </div>
          <div className="bot-message-bubble">
            {isTable ? renderTableFromText(content as string) : (
              <p className="message-text">{String(content)}</p>
            )}
          </div>
        </div>
      </div>
    );
  }
};

const renderTableFromText = (text: string) => {
  const lines = text.trim().split('\n').filter(line => line.includes('|'));
  if (lines.length < 2) {
    return <p className="message-text">{text}</p>;
  }

  const headers = lines[0].split('|').map(cell => cell.trim());
  const rows = lines.slice(1).map(row => row.split('|').map(cell => cell.trim()));

  return (
    <table className="bot-table">
      <thead>
        <tr>
          {headers.map((head, i) => <th key={i}>{head}</th>)}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, i) => (
          <tr key={i}>
            {row.map((cell, j) => <td key={j}>{cell}</td>)}
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default ChatInterface;
