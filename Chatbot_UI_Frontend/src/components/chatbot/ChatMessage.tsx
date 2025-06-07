import React from 'react';
import { Bot, User, Clock, MapPin, Package } from 'lucide-react';

export interface Message {
  id: string;
  content: string;
  isUser: boolean;
  timestamp: Date;
  intent?: string;
  data?: Record<string, any>;
}

interface ChatMessageProps {
  message: Message;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const renderMessageContent = () => {
    if (message.isUser) {
      return <p className="text-gray-800">{message.content}</p>;
    }

    // Bot message with potential rich content
    return (
      <div className="space-y-3">
        <p className="text-gray-800 whitespace-pre-line">{message.content}</p>

        {/* Render rich data if available */}
        {message.data && message.intent === 'batch_location' && (
          <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
            <div className="flex items-center gap-2 mb-2">
              <Package className="w-4 h-4 text-blue-600" />
              <span className="font-medium text-blue-800">Batch Details</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="flex items-center gap-1">
                <MapPin className="w-3 h-3 text-gray-500" />
                <span>Location: {message.data.location}</span>
              </div>
              <div className="flex items-center gap-1">
                <Clock className="w-3 h-3 text-gray-500" />
                <span>Status: {message.data.status}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`flex gap-3 ${message.isUser ? 'justify-end' : 'justify-start'}`}>
      {!message.isUser && (
        <div className="flex-shrink-0 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
          <Bot className="w-4 h-4 text-blue-600" />
        </div>
      )}

      <div className={`max-w-xs lg:max-w-md ${message.isUser ? 'order-first' : ''}`}>
        <div
          className={`p-3 rounded-lg ${
            message.isUser
              ? 'bg-blue-600 text-white'
              : 'bg-white border border-gray-200 shadow-sm'
          }`}
        >
          {renderMessageContent()}
        </div>

        <div className={`text-xs text-gray-500 mt-1 ${message.isUser ? 'text-right' : 'text-left'}`}>
          {formatTime(message.timestamp)}
        </div>
      </div>

      {message.isUser && (
        <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
          <User className="w-4 h-4 text-gray-600" />
        </div>
      )}
    </div>
  );
};