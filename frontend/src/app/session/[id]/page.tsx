'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Send, Volume2, PlayCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { VoiceButton } from '@/components/VoiceButton';
import { ChatBubble } from '@/components/ChatBubble';
import { PronunciationBadge } from '@/components/PronunciationBadge';
import { sessionApi } from '@/lib/api';
import { SessionMessage, SessionMessageReply } from '@/types/api';
import toast from 'react-hot-toast';

export default function SessionPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const sessionId = parseInt(params.id as string);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<SessionMessage[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [autoplay, setAutoplay] = useState(true);
  const [lastAssistantMessageId, setLastAssistantMessageId] = useState<number | null>(null);

  // Query session messages
  const { data: sessionData, isLoading: isLoadingSession } = useQuery({
    queryKey: ['session', sessionId],
    queryFn: async () => {
      const response = await sessionApi.getSessionById(sessionId);
      return response.data;
    },
    enabled: !!sessionId,
  });

  // Query session messages
  const { data: sessionMessages, isLoading: isLoadingMessages } = useQuery({
    queryKey: ['session-messages', sessionId],
    queryFn: async () => {
      const response = await sessionApi.getSessionMessages(sessionId);
      return response.data;
    },
    enabled: !!sessionId,
  });

  // Load messages when sessionMessages data is available
  useEffect(() => {
    if (sessionMessages && sessionMessages.length > 0) {
      setMessages(sessionMessages);
    }
  }, [sessionMessages]);

  // Mutation for sending messages
  const sendMessageMutation = useMutation({
    mutationFn: (audioBlob: Blob) => sessionApi.sendMessage(sessionId, audioBlob),
    onSuccess: (response) => {
      const data = response.data;
      
      // Add user message with pronunciation score
      const userMessage: SessionMessage = {
        id: Date.now(),
        session_id: sessionId,
        role: 'user',
        text: data.pronunciation.word_scores.map(w => w.word).join(' ') || 'Áudio enviado',
        audio_url: '', // Will be populated when we get the actual URL
        pronunciation_score: {
          ...data.pronunciation,
          provider: 'azure',
          raw: {},
        },
        created_at: new Date().toISOString(),
      };

      // Add assistant message
      const assistantMessage: SessionMessage = {
        id: Date.now() + 1,
        session_id: sessionId,
        role: 'assistant',
        text: data.reply_text,
        audio_url: data.reply_audio_url,
        pronunciation_score: {
          provider: 'azure',
          overall_score: 0,
          accuracy_score: 0,
          fluency_score: 0,
          completeness_score: 0,
          word_scores: [],
          raw: {},
        },
        created_at: new Date().toISOString(),
      };

      setMessages(prev => [...prev, userMessage, assistantMessage]);
      
      // Track the last assistant message for autoplay
      setLastAssistantMessageId(assistantMessage.id);
      
      // Show new flashcards notification
      if (data.new_flashcards.length > 0) {
        toast.success(`${data.new_flashcards.length} novos flashcards criados!`);
      }

      // Invalidate flashcards query to refresh due cards
      queryClient.invalidateQueries({ queryKey: ['due-flashcards'] });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Erro ao enviar mensagem';
      toast.error(message);
    },
    onSettled: () => {
      setIsProcessing(false);
    },
  });

  const handleRecordingComplete = async (audioBlob: Blob) => {
    console.log('=== HANDLE RECORDING COMPLETE ===');
    console.log('Audio blob size:', audioBlob.size);
    console.log('Audio blob type:', audioBlob.type);
    setIsProcessing(true);
    sendMessageMutation.mutate(audioBlob);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  if (isLoadingSession) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando sessão...</p>
        </div>
      </div>
    );
  }

  if (!sessionData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">Sessão não encontrada</p>
          <Button onClick={() => router.push('/dashboard')} className="mt-4">
            Voltar ao Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => router.push('/dashboard')}
                className="mr-4"
              >
                <ArrowLeft size={20} />
              </Button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900 capitalize">
                  Sessão: {sessionData.topic}
                </h1>
                <p className="text-sm text-gray-500">
                  {messages.length} mensagens
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant={autoplay ? "default" : "outline"}
                size="sm"
                onClick={() => setAutoplay(!autoplay)}
                className="flex items-center gap-2"
              >
                <PlayCircle size={16} />
                <span className="hidden sm:inline">Autoplay</span>
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <Volume2 size={48} className="mx-auto" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Comece a conversar!
              </h3>
              <p className="text-gray-600">
                Pressione e segure o botão de gravação para enviar sua primeira mensagem
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <ChatBubble
                  key={message.id}
                  message={message}
                  showPronunciation={message.role === 'user'}
                  autoplay={autoplay && message.role === 'assistant' && message.id === lastAssistantMessageId}
                />
              ))}
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="bg-white border-t">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-center">
            <VoiceButton
              onRecordingComplete={handleRecordingComplete}
              disabled={isProcessing}
              size="lg"
            />
          </div>
          
          {isProcessing && (
            <div className="text-center mt-4">
              <div className="inline-flex items-center">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600 mr-2"></div>
                <span className="text-sm text-gray-600">Processando sua mensagem...</span>
              </div>
            </div>
          )}

          {sendMessageMutation.error && (
            <div className="text-center mt-4">
              <p className="text-sm text-red-600">
                Erro ao processar mensagem. Tente novamente.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
