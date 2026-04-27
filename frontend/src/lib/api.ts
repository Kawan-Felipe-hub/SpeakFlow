import axios, { AxiosResponse } from 'axios';
import { 
  User, 
  TokenResponse, 
  LoginRequest, 
  RegisterRequest, 
  VoiceSession, 
  CreateSessionRequest,
  SessionMessage,
  SessionMessageReply,
  FlashCard,
  CreateFlashCardRequest,
  ReviewRequest,
  ReviewResponse,
  ApiError
} from '@/types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Important for httpOnly cookies
});

// Request interceptor to add auth token if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired, try to refresh
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
            refresh: refreshToken
          });
          const { access } = response.data;
          localStorage.setItem('access_token', access);
          
          // Retry the original request
          error.config.headers.Authorization = `Bearer ${access}`;
          return api.request(error.config);
        } catch (refreshError) {
          // Refresh failed, clear tokens and redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      } else {
        // No refresh token, redirect to login
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth APIs
export const authApi = {
  login: async (data: LoginRequest): Promise<AxiosResponse<TokenResponse>> => {
    const response = await api.post('/auth/login/', data);
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    return response;
  },
  
  register: async (data: RegisterRequest): Promise<AxiosResponse<TokenResponse>> => {
    const response = await api.post('/auth/register/', data);
    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    return response;
  },
  
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  },
  
  getCurrentUser: async (): Promise<AxiosResponse<User>> => {
    return api.get('/auth/me/');
  }
};

// Session APIs
export const sessionApi = {
  getSessions: async (): Promise<AxiosResponse<{sessions: VoiceSession[]}>> => {
    return api.get('/sessions/');
  },
  
  getSessionById: async (id: number): Promise<AxiosResponse<VoiceSession>> => {
    return api.get(`/sessions/${id}/`);
  },
  
  createSession: async (data: CreateSessionRequest): Promise<AxiosResponse<VoiceSession>> => {
    return api.post('/sessions/', data);
  },
  
  sendMessage: async (sessionId: number, audioBlob: Blob): Promise<AxiosResponse<SessionMessageReply>> => {
    console.log('=== ENVIANDO MENSAGEM ===');
    console.log('Session ID:', sessionId);
    console.log('Audio blob size:', audioBlob.size);
    console.log('Audio blob type:', audioBlob.type);
    
    const formData = new FormData();
    formData.append('audio', audioBlob, 'mensagem.webm');
    
    console.log('Enviando requisição para:', `/sessions/${sessionId}/message/`);
    
    // Não definir Content-Type manualmente - Axios define automaticamente com boundary correto
    const response = await api.post(`/sessions/${sessionId}/message/`, formData);
    
    console.log('=== RESPOSTA RECEBIDA ===');
    console.log('Status:', response.status);
    console.log('Data:', response.data);
    
    return response;
  },

  deleteSession: async (sessionId: number): Promise<AxiosResponse<void>> => {
    return api.delete(`/sessions/${sessionId}/`);
  },

  getSessionMessages: async (sessionId: number): Promise<AxiosResponse<SessionMessage[]>> => {
    return api.get(`/sessions/${sessionId}/messages/`);
  },

};

// Flashcard APIs
export const flashcardApi = {
  getFlashcards: async (): Promise<AxiosResponse<FlashCard[]>> => {
    return api.get('/flashcards/');
  },
  
  getDueFlashcards: async (): Promise<AxiosResponse<FlashCard[]>> => {
    return api.get('/flashcards/due/');
  },
  
  createFlashcard: async (data: CreateFlashCardRequest): Promise<AxiosResponse<FlashCard>> => {
    return api.post('/flashcards/', data);
  },
  
  reviewFlashcard: async (data: ReviewRequest): Promise<AxiosResponse<ReviewResponse>> => {
    return api.post('/flashcards/review/', data);
  },

  deleteFlashcard: async (flashcardId: number): Promise<AxiosResponse<void>> => {
    return api.delete(`/flashcards/${flashcardId}/`);
  }
};

// Dashboard API
export const dashboardApi = {
  getStats: async (): Promise<AxiosResponse<{
    streak: number;
    total_sessions: number;
    due_flashcards: number;
    recent_sessions: VoiceSession[];
  }>> => {
    const [sessionsResponse, dueFlashcardsResponse] = await Promise.all([
      api.get('/sessions/'),
      api.get('/flashcards/due/')
    ]);
    
    // Django Ninja retorna arrays diretamente, não objetos com .sessions ou .flashcards
    const sessions = Array.isArray(sessionsResponse.data) ? sessionsResponse.data : [];
    const dueFlashcards = Array.isArray(dueFlashcardsResponse.data) ? dueFlashcardsResponse.data : [];
    
    // Calculate streak (simplified - consecutive days with sessions)
    const streak = calculateStreak(sessions);
    
    return {
      data: {
        streak,
        total_sessions: sessions.length,
        due_flashcards: dueFlashcards.length,
        recent_sessions: sessions.slice(-5).reverse(),
      },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {} as any,
    };
  },
  
  createSession: async (topic: string = 'General Practice'): Promise<AxiosResponse<{ id: number }>> => {
    const response = await api.post('/sessions/', { topic });
    return response;
  }
};

// Helper function to calculate streak
function calculateStreak(sessions: VoiceSession[]): number {
  if (sessions.length === 0) return 0;
  
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  
  const sessionDates = sessions
    .map(s => new Date(s.started_at))
    .map(date => {
      date.setHours(0, 0, 0, 0);
      return date;
    })
    .sort((a, b) => b.getTime() - a.getTime());
  
  let streak = 0;
  let currentDate = new Date(today);
  
  for (const sessionDate of sessionDates) {
    if (sessionDate.getTime() === currentDate.getTime()) {
      streak++;
      currentDate.setDate(currentDate.getDate() - 1);
    } else if (sessionDate.getTime() < currentDate.getTime()) {
      break;
    }
  }
  
  return streak;
}

export default api;
