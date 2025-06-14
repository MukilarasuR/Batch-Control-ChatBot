// src/component/ChatUI.tsx
import React, { useState } from "react";
import { sendMessageToBot } from "../api/chatbotApi";

const ChatUI = () => {
  const [messages, setMessages] = useState<{ user: string; bot: string }[]>([]);
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setInput("");
    const botReply = await sendMessageToBot(userMessage);

    setMessages([...messages, { user: userMessage, bot: botReply }]);
  };

  return (
    <div className="max-w-xl mx-auto mt-10 font-sans">
      <h1 className="text-2xl font-bold mb-4 text-center">🔵 ERP Chatbot</h1>
      <div className="h-96 overflow-y-auto border p-4 rounded bg-white shadow">
        {messages.map((m, i) => (
          <div key={i} className="mb-3">
            <p className="text-blue-600 font-semibold">🧑 You: {m.user}</p>
            <p className="text-green-700 ml-4 whitespace-pre-line">🤖 Bot: {m.bot}</p>
          </div>
        ))}
      </div>
      <div className="flex gap-2 mt-4">
        <input
          className="border p-2 w-full rounded"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me anything about ERP data..."
        />
        <button
          onClick={handleSend}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatUI;
