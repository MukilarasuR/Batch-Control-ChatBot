import axios from "axios";

const BASE_URL = "http://localhost:8000";

export const sendMessageToBot = async (message: string) => {
  try {
    const res = await axios.post(`${BASE_URL}/chat`, {
      message, 
    });
    return res.data.response;
  } catch (error: any) {
    console.error("Chatbot API error:", error.response?.data || error.message);
    return "⚠️ Failed to connect to chatbot server.";
  }
};
