/**
 * API client for Map Dater backend
 * Connects to the FastAPI backend server
 */

// Backend API URL - change this if your backend runs on a different port
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// =============================================================================
// Map Analysis Types (Image -> Date)
// =============================================================================

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

// =============================================================================
// Game Types
// =============================================================================

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

// =============================================================================
// Map Generation Types (Date -> Image)
// =============================================================================

export interface MapGenerationEntity {
  name: string;
  canonical_name: string;
  type: string;
  valid_range: [number, number];
  confidence: number;
}

export interface UncertaintyFactor {
  type: string;
  description: string;
  severity: number;
  affected_entities: string[];
  recommendations: string[];
}

export interface MapGenerationUncertainty {
  uncertainty_score: number;
  confidence: number;
  risk_level: 'low' | 'medium' | 'high';
  factors: UncertaintyFactor[];
  notes: string[];
}

export interface MapGenerationResponse {
  date_range: [number, number];
  entities_shown: MapGenerationEntity[];
  assumptions: string[];
  uncertainty: MapGenerationUncertainty;
  confidence: number;
  risk_level: 'low' | 'medium' | 'high';
  image_base64: string | null;
  metadata: Record<string, unknown>;
}

export interface MapGenerationPreview {
  date_range: [number, number];
  is_single_year: boolean;
  midpoint: number;
  entities_count: number;
  dominant_entities: string[];
  conflicts: Array<{
    type: string;
    entities: string[];
    description: string;
  }>;
  risk_assessment: {
    risk_score: number;
    risk_level: string;
    transitional_periods: string[];
    recommendations: string[];
  };
  assumptions: string[];
}

export interface EntitiesForYearResponse {
  year: number;
  entity_count: number;
  entities: Array<{
    name: string;
    canonical_name: string;
    type: string;
    valid_range: [number, number];
  }>;
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

// =============================================================================
// Map Generation API (Date -> Image)
// =============================================================================

/**
 * Generate a historical map for a given date or date range
 */
export async function generateMap(
  date: string,
  options?: {
    includeImage?: boolean;
    format?: 'png' | 'svg';
  }
): Promise<MapGenerationResponse> {
  const params = new URLSearchParams({
    date,
    include_image: String(options?.includeImage ?? true),
    format: options?.format ?? 'svg',
  });

  const response = await fetch(`${API_BASE_URL}/generate?${params}`, {
    method: 'POST',
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to generate map: ${error}`);
  }

  return response.json();
}

/**
 * Get just the map image (returns a blob URL)
 */
export async function generateMapImage(
  date: string,
  format: 'png' | 'svg' = 'svg'
): Promise<string> {
  const params = new URLSearchParams({ date, format });

  const response = await fetch(`${API_BASE_URL}/generate/image?${params}`);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to generate map image: ${error}`);
  }

  const blob = await response.blob();
  return URL.createObjectURL(blob);
}

/**
 * Preview what would be generated without rendering
 */
export async function previewMapGeneration(
  date: string
): Promise<MapGenerationPreview> {
  const params = new URLSearchParams({ date });

  const response = await fetch(`${API_BASE_URL}/generate/preview?${params}`);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to preview map: ${error}`);
  }

  return response.json();
}

/**
 * Get all entities that existed in a specific year
 */
export async function getEntitiesForYear(
  year: number
): Promise<EntitiesForYearResponse> {
  const params = new URLSearchParams({ year: String(year) });

  const response = await fetch(`${API_BASE_URL}/generate/entities?${params}`);

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`Failed to get entities: ${error}`);
  }

  return response.json();
}
