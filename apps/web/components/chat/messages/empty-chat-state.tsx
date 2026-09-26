"use client";

import { BookOpen, HelpCircle } from "lucide-react";

interface EmptyChatStateProps {
  onSuggestedClick: (query: string) => void;
}

export default function EmptyChatState({
  onSuggestedClick,
}: EmptyChatStateProps) {
  const suggestions = [
    "What is our standard annual leave & PTO policy?",
    "How does the travel and expense reimbursement process work?",
    "What are the remote work and flexible hours guidelines?",
    "What health and wellness benefits are covered?",
  ];

  return (
    <div className="flex flex-1 flex-col items-center justify-center p-6 text-center max-w-xl mx-auto space-y-6">
      <div className="flex flex-col items-center space-y-2">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-neutral-900 text-white shadow-md dark:bg-neutral-100 dark:text-neutral-900">
          <BookOpen className="h-6 w-6" />
        </div>
        <h2 className="text-lg font-semibold tracking-tight text-neutral-900 dark:text-neutral-50">
          How can I help you today?
        </h2>
        <p className="text-xs text-neutral-500 max-w-sm">
          Ask questions about company handbooks, travel guidelines, benefits,
          and IT policies.
        </p>
      </div>

      {/* Suggestion Prompts */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full">
        {suggestions.map((prompt, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onSuggestedClick(prompt)}
            className="flex items-start text-left p-3 rounded-lg border border-neutral-200/80 bg-white hover:bg-neutral-50 hover:border-neutral-300 transition-all text-xs text-neutral-700 dark:border-neutral-800 dark:bg-neutral-950 dark:text-neutral-300 dark:hover:bg-neutral-900 shadow-2xs"
          >
            <HelpCircle className="h-4 w-4 text-neutral-400 mr-2 shrink-0 mt-0.5" />
            <span>{prompt}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
