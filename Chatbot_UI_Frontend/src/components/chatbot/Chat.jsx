import React, { useState } from "react";

function Chat() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { id: 1, role: "assistant", content: "Hello! How can I help you today?" }
  ]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    const trimmedInput = input.trim();
    if (!trimmedInput) return;

    const userMessage = {
      id: Date.now(),
      role: "user",
      content: trimmedInput,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {   // ✅ Fixed here
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: trimmedInput }),
      });

      const data = await response.json();

      const botMessage = {
        id: Date.now() + 1,
        role: "assistant",
        content: data.message || "Sorry, I didn't understand that.",
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 2,
          role: "assistant",
          content: "❌ Server error. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", fontFamily: "Arial" }}>
      <h2>📦 ERP Assistant</h2>

      <div
        style={{
          maxHeight: "300px",
          overflowY: "auto",
          border: "1px solid #ccc",
          padding: "10px",
          marginBottom: "10px",
          borderRadius: "8px",
          background: "#f9f9f9",
        }}
      >
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              textAlign: msg.role === "user" ? "right" : "left",
              margin: "5px 0",
            }}
          >
            <b>{msg.role === "user" ? "You:" : "Bot:"}</b> {msg.content}
          </div>
        ))}
        {loading && (
          <div style={{ fontStyle: "italic", color: "#888" }}>Bot is typing...</div>
        )}
      </div>

      <div style={{ display: "flex", gap: "10px" }}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Ask about a batch, employee, or product..."
          style={{
            flex: 1,
            padding: "10px",
            fontSize: "16px",
            borderRadius: "5px",
            border: "1px solid #ccc",
          }}
        />
        <button
          onClick={sendMessage}
          style={{
            padding: "10px 20px",
            fontSize: "16px",
            borderRadius: "5px",
            backgroundColor: "#007bff",
            color: "#fff",
            border: "none",
            cursor: "pointer",
          }}
          disabled={loading}
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default Chat;




// import React, { useState } from "react";

// function Chat() {
//   const [input, setInput] = useState("");
//   const [messages, setMessages] = useState([
//     { id: 1, role: "assistant", content: "Hello! How can I help you today?" }
//   ]);
//   const [loading, setLoading] = useState(false);

//   const sendMessage = async () => {
//     const trimmedInput = input.trim();
//     if (!trimmedInput) return;

//     const userMessage = {
//       id: Date.now(), // Unique ID
//       role: "user",
//       content: trimmedInput,
//     };

//     // Optimistically update chat
//     setMessages((prev) => [...prev, userMessage]);
//     setInput("");
//     setLoading(true);

//     try {
//       const response = await fetch("http://127.0.0.1:8000/api/v1/chat", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ query: trimmedInput }),
//       });

//       const data = await response.json();

//       const botMessage = {
//         id: Date.now() + 1,
//         role: "assistant",
//         content: data.message || "Sorry, I didn't understand that.",
//       };

//       setMessages((prev) => [...prev, botMessage]);
//     } catch (error) {
//       setMessages((prev) => [
//         ...prev,
//         {
//           id: Date.now() + 2,
//           role: "assistant",
//           content: "❌ Server error. Please try again.",
//         },
//       ]);
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div style={{ maxWidth: "600px", margin: "0 auto", fontFamily: "Arial" }}>
//       <h2>📦 ERP Assistant</h2>

//       <div
//         style={{
//           maxHeight: "300px",
//           overflowY: "auto",
//           border: "1px solid #ccc",
//           padding: "10px",
//           marginBottom: "10px",
//           borderRadius: "8px",
//           background: "#f9f9f9",
//         }}
//       >
//         {messages.map((msg) => (
//           <div
//             key={msg.id}
//             style={{
//               textAlign: msg.role === "user" ? "right" : "left",
//               margin: "5px 0",
//             }}
//           >
//             <b>{msg.role === "user" ? "You:" : "Bot:"}</b> {msg.content}
//           </div>
//         ))}
//         {loading && (
//           <div style={{ fontStyle: "italic", color: "#888" }}>Bot is typing...</div>
//         )}
//       </div>

//       <div style={{ display: "flex", gap: "10px" }}>
//         <input
//           type="text"
//           value={input}
//           onChange={(e) => setInput(e.target.value)}
//           onKeyDown={(e) => e.key === "Enter" && sendMessage()}
//           placeholder="Ask about a batch, employee, or product..."
//           style={{
//             flex: 1,
//             padding: "10px",
//             fontSize: "16px",
//             borderRadius: "5px",
//             border: "1px solid #ccc",
//           }}
//         />
//         <button
//           onClick={sendMessage}
//           style={{
//             padding: "10px 20px",
//             fontSize: "16px",
//             borderRadius: "5px",
//             backgroundColor: "#007bff",
//             color: "#fff",
//             border: "none",
//             cursor: "pointer",
//           }}
//           disabled={loading}
//         >
//           Send
//         </button>
//       </div>
//     </div>
//   );
// }

// export default Chat;