export interface User {
  id: number;
  username: string;
  email: string;
  total_sessions: number;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access: string;
  refresh: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface VoiceSession {
  id: number;
  user_id: number;
  started_at: string;
  ended_at: string | null;
  topic: string;
  total_messages: number;
}

export interface CreateSessionRequest {
  topic: string;
}

export interface SessionMessage {
  id: number;
  session_id: number;
  role: 'user' | 'assistant';
  text: string;
  audio_url: string;
  pronunciation_score: PronunciationScore;
  created_at: string;
}

export interface PronunciationScore {
  provider: string;
  overall_score: number;
  accuracy_score: number;
  fluency_score: number;
  completeness_score: number;
  word_scores: WordScore[];
  raw: any;
}

export interface WordScore {
  word: string;
  accuracy_score: number;
  error_type: string;
}

export interface SessionMessageReply {
  reply_text: string;
  reply_audio_url: string;
  corrections: string[];
  new_flashcards: FlashCard[];
  pronunciation: {
    overall_score: number;
    accuracy_score: number;
    fluency_score: number;
    completeness_score: number;
    word_scores: WordScore[];
  };
}

export interface FlashCard {
  id: number;
  user_id: number;
  front: string;
  back: string;
  easiness_factor: number;
  interval_days: number;
  repetitions: number;
  next_review_at: string;
  created_from_session_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface CreateFlashCardRequest {
  front: string;
  back: string;
  created_from_session_id?: number;
}

export interface ReviewRequest {
  flashcard_id: number;
  quality_score: number;
}

export interface ReviewResponse {
  flashcard: FlashCard;
  reviewed_at: string;
  quality_score: number;
  new_interval: number;
}

export interface ApiError {
  detail: string;
}

export interface DashboardStats {
  streak: number;
  total_sessions: number;
  due_flashcards: number;
  recent_sessions: VoiceSession[];
}
