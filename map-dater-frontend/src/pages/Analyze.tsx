import { useState } from 'react';
import { Link } from 'react-router-dom';
import { MapUploadPanel } from '../components/MapUploadPanel';
import { DateEstimatePanel } from '../components/DateEstimatePanel';
import { ConfidenceBar } from '../components/ConfidenceBar';
import { EvidenceCard } from '../components/EvidenceCard';
import { analyzeMap, DateEstimateResponse } from '../api/mapDaterApi';

export function Analyze() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<DateEstimateResponse | null>(null);

  const handleFileSelect = async (file: File) => {
    setIsAnalyzing(true);
    setResult(null);

    try {
      const response = await analyzeMap(file);
      setResult(response);
    } catch (error) {
      console.error('Error analyzing map:', error);
      alert('Failed to analyze map. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-parchment-100 py-8 px-4">
      {/* Header */}
      <div className="max-w-6xl mx-auto mb-8">
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
          <h1 className="text-4xl font-display font-bold text-ink mb-2">Analyze a Historical Map</h1>

          <div className="flex items-center justify-center space-x-3 mb-4">
            <div className="h-px w-16 bg-sepia-400"></div>
            <svg className="w-4 h-4 text-sepia-500" fill="currentColor" viewBox="0 0 20 20">
              <circle cx="10" cy="10" r="3" />
            </svg>
            <div className="h-px w-16 bg-sepia-400"></div>
          </div>

          <p className="text-sepia-600 font-serif max-w-2xl mx-auto">
            Upload an image of a historical map to discover when it was likely created based on cartographic features
            and historical entities.
          </p>
        </div>
      </div>

      {/* Main content */}
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Upload section */}
        <div className="bg-parchment-50 border-2 border-sepia-400 rounded-lg p-8 shadow-paper">
          <MapUploadPanel onFileSelect={handleFileSelect} isAnalyzing={isAnalyzing} />
        </div>

        {/* Results section */}
        {result && (
          <div className="space-y-8 animate-fade-in">
            {/* Date estimate */}
            <div className="bg-parchment-50 border-2 border-sepia-400 rounded-lg p-8 shadow-paper">
              <h2 className="text-2xl font-serif font-semibold text-ink mb-6 text-center">Analysis Results</h2>
              <DateEstimatePanel dateRange={result.date_range} mostLikelyYear={result.most_likely_year} />
            </div>

            {/* Confidence */}
            <div className="bg-parchment-50 border-2 border-sepia-400 rounded-lg p-8 shadow-paper">
              <h2 className="text-xl font-serif font-semibold text-ink mb-6 text-center">Confidence Assessment</h2>
              <ConfidenceBar confidence={result.confidence} />
            </div>

            {/* Evidence */}
            <div className="bg-parchment-50 border-2 border-sepia-400 rounded-lg p-8 shadow-paper">
              <h2 className="text-xl font-serif font-semibold text-ink mb-6">Historical Evidence</h2>

              <p className="text-sm text-sepia-600 font-serif mb-6 italic">
                The following temporal clues were identified on your map. Each signal constrains the possible creation
                date based on when that entity or feature existed.
              </p>

              <div className="space-y-4">
                {result.evidence.map((evidence, index) => (
                  <EvidenceCard key={index} evidence={evidence} index={index + 1} />
                ))}
              </div>

              {/* Explanation note */}
              <div className="mt-6 p-4 bg-sepia-100 border-l-4 border-sepia-600 rounded">
                <p className="text-sm text-ink-light font-serif">
                  <strong className="text-ink">How this works:</strong> Our system identifies political entities, city
                  names, and cartographic features that can be dated to specific time periods. The estimated range
                  represents the intersection of all identified temporal constraints.
                </p>
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => {
                  setResult(null);
                  setIsAnalyzing(false);
                }}
                className="px-6 py-3 bg-parchment-50 text-sepia-700 border-2 border-sepia-500 font-serif font-semibold rounded-lg shadow-paper hover:shadow-paper-lg transition-all duration-200 hover:bg-parchment-200"
              >
                Analyze Another Map
              </button>

              <Link
                to="/game"
                className="px-6 py-3 bg-sepia-600 text-parchment-50 font-serif font-semibold rounded-lg shadow-paper hover:shadow-paper-lg transition-all duration-200 hover:bg-sepia-700"
              >
                Try the Game Mode
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
