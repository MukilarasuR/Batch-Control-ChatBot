import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

export interface ChatRequest {
  query: string;
  session_id?: string;
}

export interface ChatResponse {
  success: boolean;
  message: string;
  intent: string;
  entities: Record<string, any>;
  data?: Record<string, any>;
  timestamp: string;
}

export interface BatchInfo {
  batch_code: string;
  location: string;
  status: string;
  timestamp: string;
  handler: string | null;
}

class ChatbotApiService {
  private axiosInstance;

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for loading states
    this.axiosInstance.interceptors.request.use(
      (config) => {
        console.log('API Request:', config.method?.toUpperCase(), config.url);
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor for error handling
    this.axiosInstance.interceptors.response.use(
      (response) => {
        console.log('API Response:', response.status, response.data);
        return response;
      },
      (error) => {
        console.error('API Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    try {
      // const response = await this.axiosInstance.post('/api/v1/chat', request);
      const response = await this.axiosInstance.post('/chat', request);
      return response.data;
    } catch (error: any) {
      throw new Error(`Failed to send message: ${error.response?.data?.detail || error.message}`);
    }
  }

  async getBatchInfo(batchCode: string): Promise<BatchInfo> {
    try {
      const response = await this.axiosInstance.get(`/api/v1/batch/${batchCode}`);
      return response.data;
    } catch (error: any) {
      throw new Error(`Failed to get batch info: ${error.response?.data?.detail || error.message}`);
    }
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    try {
      const response = await this.axiosInstance.get('/health');
      return response.data;
    } catch (error: any) {
      throw new Error(`Health check failed: ${error.response?.data?.detail || error.message}`);
    }
  }
}

export const chatbotApi = new ChatbotApiService();