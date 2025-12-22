import { useState } from 'react';

interface FeedbackPanelProps {
  feedback: string[];
  systemEstimate: {
    range: [number, number];
    most_likely: number;
  };
  userGuess: number | [number, number];
}

export function FeedbackPanel({ feedback, systemEstimate, userGuess }: FeedbackPanelProps) {
  const [expanded, setExpanded] = useState(true);

  const isRange = Array.isArray(userGuess);
  const guessDisplay = isRange ? `${userGuess[0]}–${userGuess[1]}` : userGuess.toString();

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Header with expand/collapse */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 bg-parchment-100 border-2 border-sepia-400 rounded-t-lg hover:bg-parchment-200 transition-colors"
      >
        <h3 className="font-serif font-semibold text-ink text-lg">Detailed Feedback</h3>
        <svg
          className={`w-5 h-5 text-sepia-600 transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expandable content */}
      {expanded && (
        <div className="border-2 border-t-0 border-sepia-400 rounded-b-lg bg-parchment-50 p-6 space-y-6">
          {/* Guess comparison */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-parchment-100 p-4 rounded border border-sepia-300">
              <div className="text-xs font-serif text-sepia-700 uppercase tracking-wide mb-2">
                Your Guess
              </div>
              <div className="text-2xl font-display font-bold text-ink">{guessDisplay}</div>
            </div>

            <div className="bg-parchment-100 p-4 rounded border border-sepia-300">
              <div className="text-xs font-serif text-sepia-700 uppercase tracking-wide mb-2">
                System Estimate
              </div>
              <div className="text-2xl font-display font-bold text-ink">
                {systemEstimate.range[0]}–{systemEstimate.range[1]}
              </div>
              <div className="text-sm text-sepia-600 mt-1">
                Most likely: {systemEstimate.most_likely}
              </div>
            </div>
          </div>

          {/* Feedback items */}
          <div className="space-y-3">
            <div className="text-sm font-serif text-sepia-700 uppercase tracking-wide mb-3">
              What We Learned:
            </div>

            {feedback.map((item, index) => (
              <div key={index} className="flex items-start space-x-3 p-3 bg-parchment-100 rounded border-l-4 border-sepia-500">
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-sepia-600 text-parchment-50 flex items-center justify-center text-xs font-serif font-semibold">
                  {index + 1}
                </div>
                <p className="flex-1 text-sm text-ink-light leading-relaxed">{item}</p>
              </div>
            ))}
          </div>

          {/* Learning tip */}
          <div className="mt-6 p-4 bg-sepia-100 border border-sepia-400 rounded">
            <div className="flex items-start space-x-2">
              <svg className="w-5 h-5 text-sepia-700 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                  clipRule="evenodd"
                />
              </svg>
              <div className="flex-1">
                <p className="text-sm font-serif text-ink font-semibold mb-1">Learning Tip</p>
                <p className="text-sm text-ink-light">
                  Focus on political entity names and city name changes. These are the most reliable temporal markers
                  for dating historical maps. Practice recognizing when major countries and cities existed under
                  different names.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
