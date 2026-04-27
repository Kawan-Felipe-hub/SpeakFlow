'use client';

import { X } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface TopicSelectionDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectTopic: (topic: string) => void;
}

const TOPICS = [
  'Job Interview',
  'Daily Meeting',
  'Airport',
  'Restaurant',
  'Small Talk',
  'Others',
];

export function TopicSelectionDialog({ isOpen, onClose, onSelectTopic }: TopicSelectionDialogProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Select Topic</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X size={20} />
          </button>
        </div>
        <div className="p-6">
          <p className="text-gray-600 mb-4">
            Choose a conversation topic to practice your English speaking skills
          </p>
          <div className="space-y-2">
            {TOPICS.map((topic) => (
              <button
                key={topic}
                onClick={() => onSelectTopic(topic)}
                className="w-full text-left px-4 py-3 rounded-lg border border-gray-200 hover:bg-gray-50 hover:border-gray-300 transition-colors"
              >
                <span className="text-gray-900 font-medium">{topic}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
