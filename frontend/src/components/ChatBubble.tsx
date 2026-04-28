import { User, Bot } from 'lucide-react';
import { useEffect, useRef } from 'react';
import { formatDateTime } from '@/lib/utils';
import { PronunciationBadge } from './PronunciationBadge';
import { SessionMessage } from '@/types/api';

interface ChatBubbleProps {
  message: SessionMessage;
  showPronunciation?: boolean;
  autoplay?: boolean;
}

export const ChatBubble = ({ message, showPronunciation = true, autoplay = false }: ChatBubbleProps) => {
  const isUser = message.role === 'user';
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (autoplay && message.audio_url && audioRef.current) {
      // Tenta reproduzir com um pequeno delay para garantir que o componente está montado
      const timer = setTimeout(() => {
        if (audioRef.current) {
          audioRef.current.play().catch(err => {
            console.log('Autoplay prevented by browser:', err);
          });
        }
      }, 100);
      
      return () => clearTimeout(timer);
    }
  }, [autoplay, message.audio_url]);
  
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'} mb-4`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser ? 'bg-primary-500' : 'bg-gray-200'
      }`}>
        {isUser ? (
          <User size={16} className="text-white" />
        ) : (
          <Bot size={16} className="text-gray-600" />
        )}
      </div>

      {/* Message content */}
      <div className={`flex flex-col gap-2 max-w-xs lg:max-w-md ${
        isUser ? 'items-end' : 'items-start'
      }`}>
        {/* Bubble */}
        <div className={`chat-bubble ${isUser ? 'user' : 'assistant'}`}>
          <p className="text-sm whitespace-pre-wrap">{message.text}</p>
          
          {/* Audio player if available (only for assistant) */}
          {!isUser && message.audio_url && (
            <audio 
              ref={audioRef}
              controls 
              className="mt-2 w-full h-8"
              src={message.audio_url}
              preload="metadata"
            >
              Your browser does not support the audio element.
            </audio>
          )}
        </div>

        {/* Pronunciation badge for user messages */}
        {isUser && showPronunciation && message.pronunciation_score && (
          <PronunciationBadge score={message.pronunciation_score} />
        )}

        {/* Timestamp */}
        <div className={`text-xs text-gray-500 ${
          isUser ? 'text-right' : 'text-left'
        }`}>
          {formatDateTime(message.created_at)}
        </div>
      </div>
    </div>
  );
};
