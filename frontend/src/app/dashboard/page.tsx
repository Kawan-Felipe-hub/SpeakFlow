'use client';

import { useQuery } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { Plus, Calendar, BookOpen, Zap } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Link } from '@/components/ui/Link';
import { dashboardApi } from '@/lib/api';
import { formatDate } from '@/lib/utils';
import { authApi } from '@/lib/api';
import toast from 'react-hot-toast';

export default function DashboardPage() {
  const router = useRouter();
  
  const { data: stats, isLoading, error } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: () => dashboardApi.getStats().then(res => res.data),
  });

  const handleCreateSession = async () => {
    try {
      // Pede pro Django criar a sessão com um tópico padrão
      const response = await dashboardApi.createSession('General Practice');
      
      // Pega o ID numérico real que o Django gerou e redireciona
      const idReal = response.data.id;
      router.push(`/session/${idReal}`);
    } catch (error) {
      console.error("Erro ao criar sessão", error);
      toast.error('Erro ao criar sessão');
    }
  };

  const handleLogout = () => {
    authApi.logout();
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
            <h3 className="text-lg font-medium text-gray-900 mb-4">Revisar Flashcards</h3>
            <p className="text-gray-600 mb-4">
              {stats?.due_flashcards || 0} cartões para revisar hoje
            </p>
            <Link href="/flashcards">
              <Button variant="outline" className="w-full">
                <BookOpen className="h-4 w-4 mr-2" />
                Revisar Agora
              </Button>
            </Link>
          </div>
        </div>

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
    </div>
  );
}
