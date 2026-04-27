'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { Plus, Calendar, BookOpen, Zap, Trash2, CheckSquare, Square, X } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Link } from '@/components/ui/Link';
import { TopicSelectionDialog } from '@/components/TopicSelectionDialog';
import { dashboardApi, sessionApi } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import { authApi } from '@/lib/api';
import toast from 'react-hot-toast';
import { VoiceSession } from '@/types/api';

export default function DashboardPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [showSessionManager, setShowSessionManager] = useState(false);
  const [showTopicDialog, setShowTopicDialog] = useState(false);
  const [selectedSessions, setSelectedSessions] = useState<Set<number>>(new Set());

  // Invalidate queries on mount to ensure fresh data when returning from sessions
  useEffect(() => {
    queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
    queryClient.invalidateQueries({ queryKey: ['all-sessions'] });
  }, [queryClient]);

  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardApi.getStats().then(res => res.data),
  });

  const { data: allSessions, isLoading: sessionsLoading } = useQuery({
    queryKey: ['all-sessions'],
    queryFn: () => sessionApi.getSessions().then(res => Array.isArray(res.data) ? res.data : []),
    enabled: showSessionManager,
  });

  const deleteMutation = useMutation({
    mutationFn: async (sessionIds: number[]) => {
      await Promise.all(sessionIds.map(id => sessionApi.deleteSession(id)));
    },
    onSuccess: () => {
      toast.success('Sessões deletadas com sucesso');
      setSelectedSessions(new Set());
      queryClient.invalidateQueries({ queryKey: ['dashboard-stats'] });
      queryClient.invalidateQueries({ queryKey: ['all-sessions'] });
    },
    onError: () => {
      toast.error('Erro ao deletar sessões');
    },
  });

  const handleCreateSession = () => {
    setShowTopicDialog(true);
  };

  const handleSelectTopic = async (topic: string) => {
    try {
      setShowTopicDialog(false);
      const response = await dashboardApi.createSession(topic);
      
      // Pega o ID numérico real que o Django gerou e redireciona
      const idReal = response.data.id;
      console.log('Sessão criada com ID:', idReal);
      router.push(`/session/${idReal}`);
    } catch (error) {
      console.error("Erro ao criar sessão", error);
      toast.error('Erro ao criar sessão');
    }
  };

  const handleLogout = () => {
    authApi.logout();
  };

  const toggleSessionSelection = (sessionId: number) => {
    setSelectedSessions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sessionId)) {
        newSet.delete(sessionId);
      } else {
        newSet.add(sessionId);
      }
      return newSet;
    });
  };

  const handleDeleteSelected = () => {
    if (selectedSessions.size === 0) {
      toast.error('Selecione pelo menos uma sessão');
      return;
    }
    if (confirm(`Tem certeza que deseja deletar ${selectedSessions.size} sessão(ões)?`)) {
      deleteMutation.mutate(Array.from(selectedSessions));
    }
  };

  const handleSelectAll = () => {
    if (allSessions && Array.isArray(allSessions) && allSessions.length > 0) {
      const allIds = allSessions.map((s: VoiceSession) => s.id);
      setSelectedSessions(new Set(allIds));
    }
  };

  const handleDeselectAll = () => {
    setSelectedSessions(new Set());
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">Erro ao carregar dashboard</p>
          <Button onClick={() => window.location.reload()} className="mt-4">
            Tentar novamente
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold text-gray-900">SpeakFlow</h1>
            <nav className="flex items-center space-x-4">
              <Link href="/flashcards" className="text-gray-600 hover:text-gray-900">
                Flashcards
              </Link>
              <Button variant="ghost" onClick={handleLogout}>
                Sair
              </Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Welcome section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Bem-vindo de volta!
          </h2>
          <p className="text-gray-600">
            Continue sua jornada de aprendizado de idiomas
          </p>
        </div>

        {/* Stats cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Zap className="h-8 w-8 text-yellow-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Sequência atual</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.streak || 0} dias</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Calendar className="h-8 w-8 text-blue-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total de sessões</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.total_sessions || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BookOpen className="h-8 w-8 text-green-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Flashcards para revisar</p>
                <p className="text-2xl font-bold text-gray-900">{stats?.due_flashcards || 0}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Iniciar nova sessão</h3>
            <p className="text-gray-600 mb-4">
              Pratique sua pronunciação e conversação com nosso tutor de IA
            </p>
            <Button onClick={handleCreateSession} className="w-full">
              <Plus className="h-4 w-4 mr-2" />
              Nova Sessão
            </Button>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Gerenciar Sessões</h3>
            <p className="text-gray-600 mb-4">
              Visualize e delete suas sessões de prática
            </p>
            <Button 
              variant="outline" 
              className="w-full"
              onClick={() => setShowSessionManager(!showSessionManager)}
            >
              {showSessionManager ? <X className="h-4 w-4 mr-2" /> : <CheckSquare className="h-4 w-4 mr-2" />}
              {showSessionManager ? 'Fechar Gerenciador' : 'Gerenciar Sessões'}
            </Button>
          </div>
        </div>

        {/* Session Manager */}
        {showSessionManager && (
          <div className="bg-white rounded-lg shadow mb-8">
            <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
              <h3 className="text-lg font-medium text-gray-900">Todas as Sessões</h3>
              <div className="flex gap-2">
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={handleSelectAll}
                  disabled={sessionsLoading || !allSessions || !Array.isArray(allSessions) || allSessions.length === 0}
                >
                  Selecionar Todas
                </Button>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={handleDeselectAll}
                  disabled={selectedSessions.size === 0}
                >
                  Limpar Seleção
                </Button>
                <Button 
                  variant="destructive" 
                  size="sm" 
                  onClick={handleDeleteSelected}
                  disabled={selectedSessions.size === 0 || deleteMutation.isPending}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Deletar ({selectedSessions.size})
                </Button>
              </div>
            </div>
            <div className="divide-y divide-gray-200">
              {sessionsLoading ? (
                <div className="px-6 py-4 text-center text-gray-500">
                  Carregando sessões...
                </div>
              ) : !allSessions || !Array.isArray(allSessions) || allSessions.length === 0 ? (
                <div className="px-6 py-4 text-center text-gray-500">
                  Nenhuma sessão encontrada
                </div>
              ) : (
                allSessions.map((session: VoiceSession) => (
                  <div key={session.id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <button
                          onClick={() => toggleSessionSelection(session.id)}
                          className="text-gray-500 hover:text-gray-700"
                        >
                          {selectedSessions.has(session.id) ? (
                            <CheckSquare className="h-5 w-5 text-blue-600" />
                          ) : (
                            <Square className="h-5 w-5" />
                          )}
                        </button>
                        <div>
                          <p className="text-sm font-medium text-gray-900 capitalize">
                            {session.topic}
                          </p>
                          <p className="text-sm text-gray-500">
                            {formatDate(session.started_at)} • {session.total_messages} mensagens
                          </p>
                        </div>
                      </div>
                      <Link href={`/session/${session.id}`}>
                        <Button variant="ghost" size="sm">
                          Ver
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Recent sessions */}
        {stats?.recent_sessions && stats.recent_sessions.length > 0 && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-medium text-gray-900">Sessões recentes</h3>
            </div>
            <div className="divide-y divide-gray-200">
              {stats.recent_sessions.map((session) => (
                <div key={session.id} className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900 capitalize">
                        {session.topic}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatDate(session.started_at)} • {session.total_messages} mensagens
                      </p>
                    </div>
                    <Link href={`/session/${session.id}`}>
                      <Button variant="ghost" size="sm">
                        Ver
                      </Button>
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Topic Selection Dialog */}
      <TopicSelectionDialog
        isOpen={showTopicDialog}
        onClose={() => setShowTopicDialog(false)}
        onSelectTopic={handleSelectTopic}
      />
    </div>
  );
}
