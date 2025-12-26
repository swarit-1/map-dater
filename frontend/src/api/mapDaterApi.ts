/**
 * API client for Map Dater backend
 * Connects to the FastAPI backend server
 */

// Backend API URL - change this if your backend runs on a different port
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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

/**
 * Upload and analyze a map image
 */
export async function analyzeMap(file: File): Promise<DateEstimateResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to analyze map: ${error}`);
  }

  return response.json();
}

/**
 * Start a new game round
 */
export async function startGameRound(
  difficulty?: 'beginner' | 'intermediate' | 'expert'
): Promise<GameRoundResponse> {
  const response = await fetch(`${API_BASE_URL}/game/start?difficulty=${difficulty || 'beginner'}`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to start game round: ${error}`);
  }

  return response.json();
}

/**
 * Submit a guess for a game round
 */
export async function submitGuess(
  roundId: string,
  guess: number | [number, number]
): Promise<GameResultResponse> {
  const response = await fetch(`${API_BASE_URL}/game/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      round_id: roundId,
      guess: guess,
    }),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to submit guess: ${error}`);
  }

  return response.json();
}
