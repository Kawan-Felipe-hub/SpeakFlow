import { User, Bot } from 'lucide-react';
import { formatDateTime } from '@/lib/utils';
import { PronunciationBadge } from './PronunciationBadge';
import { SessionMessage } from '@/types/api';

interface ChatBubbleProps {
  message: SessionMessage;
  showPronunciation?: boolean;
}

export const ChatBubble = ({ message, showPronunciation = true }: ChatBubbleProps) => {
  const isUser = message.role === 'user';
  
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
          
          {/* Audio player if available */}
          {message.audio_url && (
            <audio 
              controls 
              className="mt-2 w-full h-8"
              src={message.audio_url}
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
