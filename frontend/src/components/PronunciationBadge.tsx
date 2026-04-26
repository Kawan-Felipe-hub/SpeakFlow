import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { getPronunciationLevel, getPronunciationColor } from '@/lib/utils';
import { PronunciationScore } from '@/types/api';

interface PronunciationBadgeProps {
  score: PronunciationScore;
  showDetails?: boolean;
}

export const PronunciationBadge = ({ score, showDetails = false }: PronunciationBadgeProps) => {
  const level = getPronunciationLevel(score.overall_score);
  const colorClasses = getPronunciationColor(level);
  
  const getIcon = () => {
    switch (level) {
      case 'good':
        return <TrendingUp size={12} />;
      case 'fair':
        return <Minus size={12} />;
      case 'poor':
        return <TrendingDown size={12} />;
    }
  };

  const getLabelText = () => {
    switch (level) {
      case 'good':
        return 'Bom';
      case 'fair':
        return 'Regular';
      case 'poor':
        return 'Precisa melhorar';
    }
  };

  return (
    <div className="flex flex-col gap-1">
      <div className={`pronunciation-badge ${colorClasses} flex items-center gap-1`}>
        {getIcon()}
        <span className="text-xs font-medium">
          {getLabelText()} ({Math.round(score.overall_score)}%)
        </span>
      </div>
      
      {showDetails && (
        <div className="text-xs text-gray-600 space-y-1">
          <div>Precisão: {Math.round(score.accuracy_score)}%</div>
          <div>Fluidez: {Math.round(score.fluency_score)}%</div>
          <div>Completude: {Math.round(score.completeness_score)}%</div>
          
          {/* Problem words */}
          {score.word_scores.filter(w => w.accuracy_score < 70).length > 0 && (
            <div className="mt-2">
              <div className="font-medium text-gray-700 mb-1">Palavras para praticar:</div>
              <div className="flex flex-wrap gap-1">
                {score.word_scores
                  .filter(w => w.accuracy_score < 70)
                  .map((word, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 bg-warning-100 text-warning-800 rounded text-xs"
                    >
                      {word.word} ({Math.round(word.accuracy_score)}%)
                    </span>
                  ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
