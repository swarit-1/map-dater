/**
 * Mock API for Map Dater backend
 * Simulates the Python backend responses
 */

export interface Evidence {
  label: string;
  valid_range: [number, number];
  explanation: string;
}

export interface DateEstimateResponse {
  date_range: [number, number];
  most_likely_year: number;
  confidence: number;
  evidence: Evidence[];
}

export interface GameRoundResponse {
  round_id: string;
  map_description: string;
  difficulty: 'beginner' | 'intermediate' | 'expert';
}

export interface GameResultResponse {
  score: number;
  was_accurate: boolean;
  feedback: string[];
  system_estimate: {
    range: [number, number];
    most_likely: number;
  };
}

// Mock responses simulating backend
const mockAnalyzeResponse: DateEstimateResponse = {
  date_range: [1949, 1990],
  most_likely_year: 1970,
  confidence: 0.87,
  evidence: [
    {
      label: 'Union of Soviet Socialist Republics',
      valid_range: [1922, 1991],
      explanation: 'USSR existed from 1922 to 1991. Its presence on the map indicates creation after 1922.',
    },
    {
      label: 'East Germany',
      valid_range: [1949, 1990],
      explanation: 'German Democratic Republic existed from 1949 to 1990. Constrains map to Cold War era.',
    },
    {
      label: 'Constantinople (not Istanbul)',
      valid_range: [330, 1930],
      explanation: 'City name changed to Istanbul in 1930. Absence of new name suggests pre-1930 creation.',
    },
  ],
};

const mockGameRound: GameRoundResponse = {
  round_id: 'mock-round-001',
  map_description: 'Cold War era political map showing divided Europe',
  difficulty: 'beginner',
};

/**
 * Mock API to simulate uploading and analyzing a map
 */
export async function analyzeMap(file: File): Promise<DateEstimateResponse> {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 2000));

  // In real implementation, this would upload the file and get backend response
  console.log('Mock: Analyzing map file:', file.name);

  return mockAnalyzeResponse;
}

/**
 * Mock API to start a new game round
 */
export async function startGameRound(
  difficulty?: 'beginner' | 'intermediate' | 'expert'
): Promise<GameRoundResponse> {
  await new Promise(resolve => setTimeout(resolve, 1000));

  return {
    ...mockGameRound,
    difficulty: difficulty || 'beginner',
  };
}

/**
 * Mock API to submit a guess for a game round
 */
export async function submitGuess(
  roundId: string,
  guess: number | [number, number]
): Promise<GameResultResponse> {
  await new Promise(resolve => setTimeout(resolve, 1500));

  const isRange = Array.isArray(guess);
  const guessStart = isRange ? guess[0] : guess;
  const guessEnd = isRange ? guess[1] : guess;

  // Simulate scoring logic
  const systemStart = 1949;
  const systemEnd = 1990;
  const mostLikely = 1970;

  // Check overlap
  const overlaps = guessEnd >= systemStart && guessStart <= systemEnd;

  // Calculate score (simplified)
  let score = 0;
  if (overlaps) {
    const overlapStart = Math.max(guessStart, systemStart);
    const overlapEnd = Math.min(guessEnd, systemEnd);
    const overlapWidth = overlapEnd - overlapStart;
    const guessWidth = guessEnd - guessStart || 1;
    const overlapPct = overlapWidth / guessWidth;

    score = Math.round(overlapPct * 80 + (isRange ? 0 : 20));
  }

  // Generate feedback
  const feedback: string[] = [];

  if (score >= 80) {
    feedback.push('Excellent! Your guess overlaps significantly with the actual date range.');
    feedback.push('You correctly identified the Cold War era political entities.');
  } else if (score >= 50) {
    feedback.push('Good attempt! Your guess partially overlaps with the actual range.');
    feedback.push('You recognized some temporal clues but may have missed others.');
  } else if (guessEnd < systemStart) {
    feedback.push('You guessed too early by several decades.');
    feedback.push('Key clue you missed: USSR and East Germany both visible on the map.');
    feedback.push('These entities did not coexist before 1949.');
  } else if (guessStart > systemEnd) {
    feedback.push('You guessed too late.');
    feedback.push('Key clue: East Germany dissolved in 1990, suggesting an earlier date.');
  } else {
    feedback.push('Your guess is in the right ballpark but could be more precise.');
    feedback.push('Try narrowing your range by looking for more specific temporal markers.');
  }

  if (!isRange && overlaps) {
    feedback.push('Bonus tip: Precise single-year guesses earn more points when correct!');
  }

  return {
    score,
    was_accurate: overlaps,
    feedback,
    system_estimate: {
      range: [systemStart, systemEnd],
      most_likely: mostLikely,
    },
  };
}
