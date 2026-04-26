import { useState } from 'react';
import { Volume2, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { FlashCard } from '@/types/api';

interface FlashCardReviewProps {
  flashcard: FlashCard;
  onReview: (quality: number) => void;
  onNext?: () => void;
}

export const FlashCardReview = ({ flashcard, onReview, onNext }: FlashCardReviewProps) => {
  const [isFlipped, setIsFlipped] = useState(false);
  const [hasReviewed, setHasReviewed] = useState(false);

  const handleFlip = () => {
    setIsFlipped(!isFlipped);
  };

  const handleReview = (quality: number) => {
    onReview(quality);
    setHasReviewed(true);
  };

  const handleNext = () => {
    setIsFlipped(false);
    setHasReviewed(false);
    onNext?.();
  };

  const qualityOptions = [
    { value: 5, label: 'Perfeito', color: 'bg-success-500 hover:bg-success-600' },
    { value: 4, label: 'Bom', color: 'bg-success-400 hover:bg-success-500' },
    { value: 3, label: 'Regular', color: 'bg-warning-500 hover:bg-warning-600' },
    { value: 2, label: 'Difícil', color: 'bg-warning-400 hover:bg-warning-500' },
    { value: 1, label: 'Muito difícil', color: 'bg-danger-500 hover:bg-danger-600' },
  ];

  return (
    <div className="max-w-md mx-auto">
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        {/* Card */}
        <div className="relative h-64 cursor-pointer" onClick={handleFlip}>
          <div className={`absolute inset-0 flex items-center justify-center p-6 transition-transform duration-500 ${
            isFlipped ? 'rotate-y-180' : ''
          }`}>
            {!isFlipped ? (
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-700 mb-2">Frente</h3>
                <p className="text-xl text-gray-900">{flashcard.front}</p>
              </div>
            ) : (
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-700 mb-2">Verso</h3>
                <p className="text-xl text-gray-900">{flashcard.back}</p>
              </div>
            )}
          </div>
        </div>

        {/* Card info */}
        <div className="px-6 py-4 bg-gray-50 border-t">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <div>
              Repetições: {flashcard.repetitions}
            </div>
            <div>
              Próxima revisão: {new Date(flashcard.next_review_at).toLocaleDateString('pt-BR')}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="p-6 space-y-4">
          {!hasReviewed ? (
            <>
              {/* Flip button */}
              <Button
                onClick={handleFlip}
                variant="outline"
                className="w-full"
              >
                <RotateCcw size={16} className="mr-2" />
                {isFlipped ? 'Ver frente' : 'Ver verso'}
              </Button>

              {/* Quality buttons - only show when flipped */}
              {isFlipped && (
                <div className="space-y-2">
                  <h4 className="text-sm font-medium text-gray-700 text-center">
                    Como foi sua lembrança?
                  </h4>
                  <div className="grid grid-cols-2 gap-2">
                    {qualityOptions.map((option) => (
                      <Button
                        key={option.value}
                        onClick={() => handleReview(option.value)}
                        className={option.color}
                        size="sm"
                      >
                        {option.label}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="text-center">
              <div className="mb-4 text-green-600 font-medium">
                ✓ Cartão revisado!
              </div>
              {onNext && (
                <Button onClick={handleNext} className="w-full">
                  Próximo cartão
                </Button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
