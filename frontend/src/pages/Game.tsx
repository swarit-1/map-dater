import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { GameMapFrame } from '../components/GameMapFrame';
import { ScoreSeal } from '../components/ScoreSeal';
import { FeedbackPanel } from '../components/FeedbackPanel';
import { startGameRound, submitGuess } from '../api/mapDaterApi';
import type { GameRoundResponse, GameResultResponse } from '../api/mapDaterApi';

type GuessType = 'single' | 'range';

export function Game() {
  const [gameRound, setGameRound] = useState<GameRoundResponse | null>(null);
  const [guessType, setGuessType] = useState<GuessType>('range');
  const [singleYear, setSingleYear] = useState('');
  const [rangeStart, setRangeStart] = useState('');
  const [rangeEnd, setRangeEnd] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<GameResultResponse | null>(null);
  const [submittedGuess, setSubmittedGuess] = useState<number | [number, number] | null>(null);

  useEffect(() => {
    loadNewRound();
  }, []);

  const loadNewRound = async () => {
    setResult(null);
    setSubmittedGuess(null);
    setSingleYear('');
    setRangeStart('');
    setRangeEnd('');

    try {
      const round = await startGameRound('beginner');
      setGameRound(round);
    } catch (error) {
      console.error('Error loading game round:', error);
    }
  };

  const handleSubmit = async () => {
    if (!gameRound) return;

    let guess: number | [number, number];

    if (guessType === 'single') {
      const year = parseInt(singleYear);
      if (isNaN(year) || year < 1000 || year > 2100) {
        alert('Please enter a valid year between 1000 and 2100');
        return;
      }
      guess = year;
    } else {
      const start = parseInt(rangeStart);
      const end = parseInt(rangeEnd);

      if (isNaN(start) || isNaN(end)) {
        alert('Please enter valid years for both start and end of range');
        return;
      }

      if (start >= end) {
        alert('Start year must be less than end year');
        return;
      }

      if (start < 1000 || end > 2100) {
        alert('Please enter years between 1000 and 2100');
        return;
      }

      guess = [start, end];
    }

    setIsSubmitting(true);
    setSubmittedGuess(guess);

    try {
      const response = await submitGuess(gameRound.round_id, guess);
      setResult(response);
    } catch (error) {
      console.error('Error submitting guess:', error);
      alert('Failed to submit guess. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const canSubmit = guessType === 'single' ? singleYear !== '' : rangeStart !== '' && rangeEnd !== '';

  return (
    <div className="min-h-screen bg-parchment-100 py-8 px-4">
      {/* Header */}
      <div className="max-w-4xl mx-auto mb-8">
        <Link
          to="/"
          className="inline-flex items-center space-x-2 text-sepia-700 hover:text-sepia-900 font-serif transition-colors"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span>Back to Home</span>
        </Link>

        <div className="mt-6 text-center">
          <h1 className="text-4xl font-display font-bold text-ink mb-2">Map Dating Game</h1>

          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="h-px w-16 bg-sepia-400"></div>
            <svg className="w-4 h-4 text-sepia-500" fill="currentColor" viewBox="0 0 20 20">
              <circle cx="10" cy="10" r="3" />
            </svg>
            <div className="h-px w-16 bg-sepia-400"></div>
          </div>

          <p className="text-sepia-600 font-serif max-w-2xl mx-auto">
            Test your knowledge of historical cartography! Make your best guess about when this map was created.
          </p>
        </div>
      </div>

      {/* Main content */}
      {gameRound && (
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Map display */}
          <div className="bg-parchment-50 border-2 border-sepia-400 rounded-lg p-8 shadow-paper">
            <GameMapFrame description={gameRound.map_description} difficulty={gameRound.difficulty} />
          </div>

          {/* Guess input (only show before submission) */}
          {!result && (
            <div className="bg-parchment-50 border-2 border-sepia-400 rounded-lg p-8 shadow-paper">
              <h2 className="text-2xl font-serif font-semibold text-ink mb-6 text-center">Make Your Guess</h2>

              {/* Guess type selector */}
              <div className="flex justify-center space-x-4 mb-6">
                <button
                  onClick={() => setGuessType('range')}
                  className={`px-6 py-2 font-serif rounded-lg border-2 transition-all ${
                    guessType === 'range'
                      ? 'bg-sepia-600 text-parchment-50 border-sepia-600'
                      : 'bg-parchment-100 text-sepia-700 border-sepia-400 hover:border-sepia-500'
                  }`}
                >
                  Year Range
                </button>

                <button
                  onClick={() => setGuessType('single')}
                  className={`px-6 py-2 font-serif rounded-lg border-2 transition-all ${
                    guessType === 'single'
                      ? 'bg-sepia-600 text-parchment-50 border-sepia-600'
                      : 'bg-parchment-100 text-sepia-700 border-sepia-400 hover:border-sepia-500'
                  }`}
                >
                  Single Year
                </button>
              </div>

              {/* Input fields */}
              <div className="max-w-md mx-auto">
                {guessType === 'single' ? (
                  <div>
                    <label className="block text-sm font-serif text-sepia-700 mb-2">Guessed Year</label>
                    <input
                      type="number"
                      value={singleYear}
                      onChange={e => setSingleYear(e.target.value)}
                      placeholder="e.g., 1945"
                      min="1000"
                      max="2100"
                      className="w-full px-4 py-3 bg-parchment-100 border-2 border-sepia-400 rounded-lg font-serif text-ink text-center text-2xl focus:outline-none focus:border-sepia-600 transition-colors"
                    />
                    <p className="text-xs text-sepia-600 mt-2 italic text-center">
                      Precise guesses earn more points when correct!
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-serif text-sepia-700 mb-2">Start Year</label>
                      <input
                        type="number"
                        value={rangeStart}
                        onChange={e => setRangeStart(e.target.value)}
                        placeholder="e.g., 1940"
                        min="1000"
                        max="2100"
                        className="w-full px-4 py-3 bg-parchment-100 border-2 border-sepia-400 rounded-lg font-serif text-ink text-center text-xl focus:outline-none focus:border-sepia-600 transition-colors"
                      />
                    </div>

                    <div className="text-center text-sepia-500 font-serif">to</div>

                    <div>
                      <label className="block text-sm font-serif text-sepia-700 mb-2">End Year</label>
                      <input
                        type="number"
                        value={rangeEnd}
                        onChange={e => setRangeEnd(e.target.value)}
                        placeholder="e.g., 1960"
                        min="1000"
                        max="2100"
                        className="w-full px-4 py-3 bg-parchment-100 border-2 border-sepia-400 rounded-lg font-serif text-ink text-center text-xl focus:outline-none focus:border-sepia-600 transition-colors"
                      />
                    </div>

                    <p className="text-xs text-sepia-600 mt-2 italic text-center">
                      Wider ranges are safer but score fewer points
                    </p>
                  </div>
                )}
              </div>

              {/* Submit button */}
              <div className="mt-8 text-center">
                <button
                  onClick={handleSubmit}
                  disabled={!canSubmit || isSubmitting}
                  className={`px-8 py-4 font-serif font-semibold text-lg rounded-lg shadow-paper transition-all ${
                    canSubmit && !isSubmitting
                      ? 'bg-sepia-600 text-parchment-50 hover:bg-sepia-700 hover:shadow-paper-lg'
                      : 'bg-sepia-300 text-parchment-200 cursor-not-allowed'
                  }`}
                >
                  {isSubmitting ? 'Submitting...' : 'Submit Guess'}
                </button>
              </div>
            </div>
          )}

          {/* Results (after submission) */}
          {result && submittedGuess && (
            <div className="space-y-8 animate-fade-in">
              {/* Score display */}
              <div className="bg-parchment-50 border-2 border-sepia-400 rounded-lg p-8 shadow-paper">
                <h2 className="text-2xl font-serif font-semibold text-ink mb-8 text-center">Your Score</h2>
                <ScoreSeal score={result.score} wasAccurate={result.was_accurate} />
              </div>

              {/* Feedback panel */}
              <FeedbackPanel
                feedback={result.feedback}
                systemEstimate={result.system_estimate}
                userGuess={submittedGuess}
              />

              {/* Action buttons */}
              <div className="flex justify-center space-x-4">
                <button
                  onClick={loadNewRound}
                  className="px-6 py-3 bg-sepia-600 text-parchment-50 font-serif font-semibold rounded-lg shadow-paper hover:shadow-paper-lg transition-all duration-200 hover:bg-sepia-700"
                >
                  Play Again
                </button>

                <Link
                  to="/analyze"
                  className="px-6 py-3 bg-parchment-50 text-sepia-700 border-2 border-sepia-500 font-serif font-semibold rounded-lg shadow-paper hover:shadow-paper-lg transition-all duration-200 hover:bg-parchment-200"
                >
                  Analyze Your Own Map
                </Link>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
