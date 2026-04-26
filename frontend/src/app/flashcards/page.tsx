'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { BookOpen, RotateCcw, CheckCircle, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { FlashCardReview } from '@/components/FlashCardReview';
import { flashcardApi } from '@/lib/api';
import { FlashCard, ReviewRequest } from '@/types/api';
import toast from 'react-hot-toast';

export default function FlashcardsPage() {
  const queryClient = useQueryClient();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isReviewing, setIsReviewing] = useState(false);
  const [totalInitialCards, setTotalInitialCards] = useState(0);
  const [reviewedCount, setReviewedCount] = useState(0);

  // Query due flashcards
  const { data: dueFlashcards = [], isLoading, error, refetch } = useQuery({
    queryKey: ['due-flashcards'],
    queryFn: () => flashcardApi.getDueFlashcards().then(res => res.data),
  });

  // Query all flashcards for stats
  const { data: allFlashcards = [] } = useQuery({
    queryKey: ['flashcards'],
    queryFn: () => flashcardApi.getFlashcards().then(res => res.data),
  });

  // Mutation for reviewing flashcards
  const reviewMutation = useMutation({
    mutationFn: (data: ReviewRequest) => flashcardApi.reviewFlashcard(data),
    onSuccess: () => {
      toast.success('Flashcard revisado!');
      setReviewedCount(prev => prev + 1);
      
      // Move to next card BEFORE invalidating queries
      setCurrentIndex(prev => {
        const newLength = dueFlashcards.length - 1;
        if (newLength <= 0) {
          setIsReviewing(false);
          setReviewedCount(0);
          return 0;
        }
        // Move to next card, but don't exceed the new array length
        return Math.min(prev + 1, newLength - 1);
      });
      
      // Invalidate queries after adjusting index
      queryClient.invalidateQueries({ queryKey: ['due-flashcards'] });
      queryClient.invalidateQueries({ queryKey: ['flashcards'] });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Erro ao revisar flashcard';
      toast.error(message);
    },
  });

  // Mutation for deleting flashcards
  const deleteMutation = useMutation({
    mutationFn: (flashcardId: number) => flashcardApi.deleteFlashcard(flashcardId),
    onSuccess: () => {
      toast.success('Flashcard excluído!');
      
      // Adjust current index BEFORE invalidating queries
      if (isReviewing) {
        setCurrentIndex(prev => {
          const newLength = dueFlashcards.length - 1;
          if (newLength <= 0) {
            setIsReviewing(false);
            setReviewedCount(0);
            return 0;
          }
          // Stay at same index (next card shifts into this position)
          return Math.min(prev, newLength - 1);
        });
      }
      
      // Invalidate queries after adjusting index
      queryClient.invalidateQueries({ queryKey: ['due-flashcards'] });
      queryClient.invalidateQueries({ queryKey: ['flashcards'] });
    },
    onError: (error: any) => {
      const message = error.response?.data?.detail || 'Erro ao excluir flashcard';
      toast.error(message);
    },
  });

  const handleDelete = (flashcardId: number) => {
    if (window.confirm('Tem certeza que deseja excluir este flashcard?')) {
      deleteMutation.mutate(flashcardId);
    }
  };

  const handleDeleteFromReview = () => {
    const currentCard = dueFlashcards[currentIndex];
    if (currentCard) {
      deleteMutation.mutate(currentCard.id);
    }
  };

  const handleStartReview = () => {
    if (dueFlashcards.length === 0) return;
    setIsReviewing(true);
    setCurrentIndex(0);
    setTotalInitialCards(dueFlashcards.length);
    setReviewedCount(0);
  };

  const handleReview = (quality: number) => {
    const currentCard = dueFlashcards[currentIndex];
    reviewMutation.mutate({
      flashcard_id: currentCard.id,
      quality_score: quality,
    });
  };

  const handleNext = () => {
    if (currentIndex < dueFlashcards.length - 1) {
      setCurrentIndex(prev => prev + 1);
    } else {
      setIsReviewing(false);
      setCurrentIndex(0);
      setTotalInitialCards(0);
      refetch();
    }
  };

  // Ensure currentIndex is always within bounds when array changes
  useEffect(() => {
    if (isReviewing && dueFlashcards.length > 0 && currentIndex >= dueFlashcards.length) {
      setCurrentIndex(dueFlashcards.length - 1);
    }
  }, [dueFlashcards.length, currentIndex, isReviewing]);

  const currentCard = dueFlashcards[currentIndex];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando flashcards...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600">Erro ao carregar flashcards</p>
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
            <h1 className="text-2xl font-bold text-gray-900">Flashcards</h1>
            <Button variant="ghost" onClick={() => window.location.href = '/dashboard'}>
              Voltar
            </Button>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <BookOpen className="h-8 w-8 text-blue-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total de flashcards</p>
                <p className="text-2xl font-bold text-gray-900">{allFlashcards.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <RotateCcw className="h-8 w-8 text-yellow-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Para revisar hoje</p>
                <p className="text-2xl font-bold text-gray-900">{dueFlashcards.length}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <CheckCircle className="h-8 w-8 text-green-500" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Progresso da revisão</p>
                <p className="text-2xl font-bold text-gray-900">
                  {isReviewing ? `${reviewedCount}/${totalInitialCards}` : `0/${dueFlashcards.length}`}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Review section */}
        {!isReviewing ? (
          <div className="text-center">
            {dueFlashcards.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-8">
                <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Parabéns!
                </h2>
                <p className="text-gray-600 mb-6">
                  Você não tem flashcards para revisar hoje.
                </p>
                <Button onClick={() => window.location.href = '/dashboard'}>
                  Voltar ao Dashboard
                </Button>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-8">
                <BookOpen className="h-16 w-16 text-blue-500 mx-auto mb-4" />
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Hora de revisar!
                </h2>
                <p className="text-gray-600 mb-6">
                  Você tem {dueFlashcards.length} flashcards para revisar hoje.
                </p>
                <Button onClick={handleStartReview} size="lg">
                  <RotateCcw className="h-5 w-5 mr-2" />
                  Começar Revisão
                </Button>
              </div>
            )}
          </div>
        ) : (
          <div>
            {/* Progress bar */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Progresso da revisão
                </span>
                <span className="text-sm text-gray-500">
                  {reviewedCount} / {totalInitialCards}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(reviewedCount / totalInitialCards) * 100}%` }}
                />
              </div>
            </div>

            {/* Flashcard review */}
            {currentCard && (
              <FlashCardReview
                flashcard={currentCard}
                onReview={handleReview}
                onNext={handleNext}
                onDelete={handleDeleteFromReview}
              />
            )}
          </div>
        )}

        {/* All flashcards list */}
        {!isReviewing && allFlashcards.length > 0 && (
          <div className="mt-8">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Todos os flashcards</h3>
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <div className="divide-y divide-gray-200">
                {allFlashcards.map((flashcard) => (
                  <div key={flashcard.id} className="px-6 py-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900 mb-1">
                          {flashcard.front}
                        </p>
                        <p className="text-sm text-gray-600">
                          {flashcard.back}
                        </p>
                        <div className="mt-2 flex items-center space-x-4 text-xs text-gray-500">
                          <span>Repetições: {flashcard.repetitions}</span>
                          <span>Intervalo: {flashcard.interval_days} dias</span>
                          <span>Próxima revisão: {new Date(flashcard.next_review_at).toLocaleDateString('pt-BR')}</span>
                        </div>
                      </div>
                      <Button
                        onClick={() => handleDelete(flashcard.id)}
                        variant="ghost"
                        size="sm"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                      >
                        <Trash2 size={16} />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
