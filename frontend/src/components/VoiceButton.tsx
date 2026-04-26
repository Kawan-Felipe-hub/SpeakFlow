import { Mic, MicOff, Pause, Play } from 'lucide-react';
import { useEffect, useRef } from 'react';
import { Button } from '@/components/ui/Button';
import { useVoiceRecorder } from '@/hooks/useVoiceRecorder';
import { cn } from '@/lib/utils';

interface VoiceButtonProps {
  onRecordingComplete?: (audioBlob: Blob) => void;
  disabled?: boolean;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const VoiceButton = ({
  onRecordingComplete,
  disabled = false,
  size = 'md',
  className
}: VoiceButtonProps) => {
  const {
    isRecording,
    isPaused,
    duration,
    audioBlob,
    startRecording,
    stopRecording,
    pauseRecording,
    resumeRecording,
    error
  } = useVoiceRecorder();

  // ✅ CRIAMOS A MEMÓRIA PARA EVITAR O LOOP INFINITO
  const blobProcessado = useRef<Blob | null>(null);

  const handleButtonClick = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  useEffect(() => {
    // Só envia se existir um áudio, não estiver gravando, E se esse áudio já não tiver sido enviado
    if (audioBlob && !isRecording && blobProcessado.current !== audioBlob) {
      
      // Debug: verificar o tamanho do blob
      console.log(`VoiceButton: received blob of ${audioBlob.size} bytes`);
      
      if (audioBlob.size < 1000) {
        console.warn('Audio blob seems too small, possible recording issue');
      }
      
      // Salva na memória que esse áudio específico já foi processado
      blobProcessado.current = audioBlob; 
      
      if (onRecordingComplete) {
        onRecordingComplete(audioBlob);
      }
    }
  }, [audioBlob, onRecordingComplete, isRecording]);

  const sizeClasses = {
    sm: 'w-12 h-12',
    md: 'w-16 h-16',
    lg: 'w-20 h-20'
  };

  const iconSizes = {
    sm: 16,
    md: 24,
    lg: 32
  };

  return (
    <div className={cn('flex flex-col items-center gap-2', className)}>
      <Button
        onClick={handleButtonClick}
        disabled={disabled || !!error}
        className={cn(
          'voice-button',
          sizeClasses[size],
          isRecording && 'recording bg-red-500 hover:bg-red-600', // Adicionei cor para ficar óbvio
          !isRecording && 'ready'
        )}
      >
        {isRecording ? (
          isPaused ? (
            <Play size={iconSizes[size]} className="text-white" />
          ) : (
            <Pause size={iconSizes[size]} className="text-white" />
          )
        ) : (
          <Mic size={iconSizes[size]} />
        )}
      </Button>

      {isRecording && (
        <div className="text-center">
          <div className="text-sm font-medium text-gray-600">
            {isPaused ? 'Pausado' : 'Gravando...'}
          </div>
          <div className="text-xs text-gray-500">
            {Math.floor(duration / 60)}:{(duration % 60).toString().padStart(2, '0')}
          </div>
        </div>
      )}

      {error && (
        <div className="text-xs text-red-600 text-center max-w-xs">
          {error}
        </div>
      )}

      {isRecording && (
        <div className="flex gap-2">
          <Button
            onClick={isPaused ? resumeRecording : pauseRecording}
            variant="ghost"
            size="icon"
            className="w-8 h-8"
          >
            {isPaused ? (
              <Play size={16} />
            ) : (
              <Pause size={16} />
            )}
          </Button>
        </div>
      )}
    </div>
  );
};
