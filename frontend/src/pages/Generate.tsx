import { useState } from 'react';
import { Link } from 'react-router-dom';
import { generateMap } from '../api/mapDaterApi';
import type { MapGenerationResponse } from '../api/mapDaterApi';

export function Generate() {
  const [dateInput, setDateInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<MapGenerationResponse | null>(null);

  const handleGenerate = async () => {
    if (!dateInput.trim()) {
      setError('Please enter a year or date range');
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await generateMap(dateInput, {
        includeImage: true,
        format: 'svg',
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate map');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleGenerate();
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'low':
        return 'text-green-600 bg-green-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'high':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="min-h-screen bg-parchment-100 p-6">
      {/* Header */}
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <Link
            to="/"
            className="flex items-center text-sepia-600 hover:text-sepia-800 transition-colors"
          >
            <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span className="font-serif">Back to Home</span>
          </Link>

          <h1 className="text-3xl font-display font-bold text-ink">Generate Historical Map</h1>

          <div className="w-24" /> {/* Spacer for alignment */}
        </div>

        {/* Description */}
        <div className="text-center mb-8">
          <p className="text-sepia-700 font-serif max-w-2xl mx-auto">
            Enter a year or date range to generate a historically accurate world map showing political
            entities that existed during that time period.
          </p>
        </div>

        {/* Input Section */}
        <div className="max-w-xl mx-auto mb-8">
          <div className="bg-parchment-50 rounded-lg shadow-paper p-6 border border-sepia-200">
            <label className="block text-sm font-serif font-semibold text-sepia-700 mb-2">
              Year or Date Range
            </label>
            <div className="flex gap-4">
              <input
                type="text"
                value={dateInput}
                onChange={(e) => setDateInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="e.g., 1914 or 1918-1939"
                className="flex-1 px-4 py-3 border border-sepia-300 rounded-lg font-serif text-lg focus:outline-none focus:ring-2 focus:ring-sepia-400 bg-white"
              />
              <button
                onClick={handleGenerate}
                disabled={isLoading}
                className="px-6 py-3 bg-sepia-600 text-parchment-50 font-serif font-semibold rounded-lg hover:bg-sepia-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <span className="flex items-center">
                    <svg className="animate-spin -ml-1 mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Generating...
                  </span>
                ) : (
                  'Generate Map'
                )}
              </button>
            </div>
            <p className="mt-2 text-sm text-sepia-500">
              Supports single years (1914) or ranges (1918-1939)
            </p>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="max-w-xl mx-auto mb-8">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-700 font-serif">{error}</p>
            </div>
          </div>
        )}

        {/* Results Section */}
        {result && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Map Display */}
            <div className="lg:col-span-2">
              <div className="bg-parchment-50 rounded-lg shadow-paper p-4 border border-sepia-200">
                <h2 className="text-xl font-display font-semibold text-ink mb-4">
                  World Map: {result.date_range[0]}
                  {result.date_range[0] !== result.date_range[1] && `-${result.date_range[1]}`}
                </h2>

                {result.image_base64 && (
                  <div className="bg-white rounded border border-sepia-200 p-2 overflow-auto">
                    <img
                      src={`data:image/svg+xml;base64,${result.image_base64}`}
                      alt={`Historical map for ${result.date_range[0]}`}
                      className="w-full h-auto"
                    />
                  </div>
                )}

                {/* Download button */}
                {result.image_base64 && (
                  <div className="mt-4 flex justify-end">
                    <a
                      href={`data:image/svg+xml;base64,${result.image_base64}`}
                      download={`map_${result.date_range[0]}.svg`}
                      className="px-4 py-2 bg-sepia-100 text-sepia-700 font-serif rounded hover:bg-sepia-200 transition-colors flex items-center"
                    >
                      <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      Download SVG
                    </a>
                  </div>
                )}
              </div>
            </div>

            {/* Sidebar Info */}
            <div className="space-y-6">
              {/* Confidence & Risk */}
              <div className="bg-parchment-50 rounded-lg shadow-paper p-4 border border-sepia-200">
                <h3 className="text-lg font-display font-semibold text-ink mb-3">Assessment</h3>

                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-serif text-sepia-600">Confidence</span>
                    <div className="flex items-center mt-1">
                      <div className="flex-1 h-2 bg-sepia-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-sepia-600 rounded-full"
                          style={{ width: `${result.confidence * 100}%` }}
                        />
                      </div>
                      <span className="ml-2 text-sm font-semibold text-sepia-700">
                        {Math.round(result.confidence * 100)}%
                      </span>
                    </div>
                  </div>

                  <div>
                    <span className="text-sm font-serif text-sepia-600">Risk Level</span>
                    <div className="mt-1">
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold ${getRiskLevelColor(result.risk_level)}`}>
                        {result.risk_level.toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Entities Shown */}
              <div className="bg-parchment-50 rounded-lg shadow-paper p-4 border border-sepia-200">
                <h3 className="text-lg font-display font-semibold text-ink mb-3">
                  Entities Shown ({result.entities_shown.length})
                </h3>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {result.entities_shown.map((entity, index) => (
                    <div
                      key={index}
                      className="flex justify-between items-center text-sm py-1 border-b border-sepia-100 last:border-0"
                    >
                      <span className="font-serif text-ink">{entity.name}</span>
                      <span className="text-sepia-500 text-xs">
                        {entity.valid_range[0]}-{entity.valid_range[1]}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Uncertainty Factors */}
              {result.uncertainty.factors.length > 0 && (
                <div className="bg-parchment-50 rounded-lg shadow-paper p-4 border border-sepia-200">
                  <h3 className="text-lg font-display font-semibold text-ink mb-3">
                    Uncertainty Factors
                  </h3>
                  <div className="space-y-2">
                    {result.uncertainty.factors.slice(0, 3).map((factor, index) => (
                      <div key={index} className="text-sm">
                        <div className="flex items-start">
                          <span className="inline-block w-2 h-2 rounded-full bg-yellow-500 mt-1.5 mr-2 flex-shrink-0" />
                          <span className="font-serif text-sepia-700">{factor.description}</span>
                        </div>
                      </div>
                    ))}
                    {result.uncertainty.factors.length > 3 && (
                      <p className="text-xs text-sepia-500 italic">
                        +{result.uncertainty.factors.length - 3} more factors
                      </p>
                    )}
                  </div>
                </div>
              )}

              {/* Assumptions */}
              {result.assumptions.length > 0 && (
                <div className="bg-parchment-50 rounded-lg shadow-paper p-4 border border-sepia-200">
                  <h3 className="text-lg font-display font-semibold text-ink mb-3">
                    Assumptions Made
                  </h3>
                  <ul className="space-y-1 text-sm text-sepia-700 font-serif">
                    {result.assumptions.slice(0, 3).map((assumption, index) => (
                      <li key={index} className="flex items-start">
                        <span className="mr-2">•</span>
                        <span>{assumption}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Info Footer */}
        {!result && !isLoading && (
          <div className="max-w-2xl mx-auto text-center mt-12">
            <div className="bg-parchment-50 rounded-lg shadow-paper p-6 border border-sepia-200">
              <h3 className="text-lg font-display font-semibold text-ink mb-3">
                About Map Generation
              </h3>
              <p className="text-sm text-sepia-700 font-serif mb-4">
                This feature is the inverse of map dating. Instead of determining when a map was
                created, you provide a date and the system generates a historically accurate
                representation of the world at that time.
              </p>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div className="text-left">
                  <h4 className="font-semibold text-sepia-800">Features:</h4>
                  <ul className="text-sepia-600 mt-1 space-y-1">
                    <li>• Political entities for any year</li>
                    <li>• Uncertainty assessment</li>
                    <li>• Historical assumptions explained</li>
                  </ul>
                </div>
                <div className="text-left">
                  <h4 className="font-semibold text-sepia-800">Examples:</h4>
                  <ul className="text-sepia-600 mt-1 space-y-1">
                    <li>• 1914 (WWI start)</li>
                    <li>• 1949-1990 (Cold War)</li>
                    <li>• 1989-1993 (Soviet collapse)</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
