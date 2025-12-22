interface ConfidenceBarProps {
  confidence: number; // 0-1
}

export function ConfidenceBar({ confidence }: ConfidenceBarProps) {
  const percentage = Math.round(confidence * 100);

  const getConfidenceLabel = (conf: number): string => {
    if (conf >= 0.9) return 'Very High';
    if (conf >= 0.75) return 'High';
    if (conf >= 0.6) return 'Moderate';
    if (conf >= 0.4) return 'Low';
    return 'Very Low';
  };

  const getConfidenceColor = (conf: number): string => {
    if (conf >= 0.75) return 'bg-sepia-600';
    if (conf >= 0.5) return 'bg-sepia-500';
    return 'bg-sepia-400';
  };

  return (
    <div className="w-full max-w-md mx-auto">
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-serif text-ink-light">Confidence</span>
        <span className="text-sm font-serif text-ink font-semibold">
          {percentage}% ({getConfidenceLabel(confidence)})
        </span>
      </div>

      <div className="relative h-8 bg-parchment-200 rounded border border-sepia-300 overflow-hidden shadow-emboss">
        {/* Ink wash effect */}
        <div
          className={`
            absolute inset-y-0 left-0 ${getConfidenceColor(confidence)}
            transition-all duration-1000 ease-out
            opacity-90
          `}
          style={{
            width: `${percentage}%`,
            background: `linear-gradient(to right,
              rgba(140, 111, 61, 0.9),
              rgba(140, 111, 61, 0.7),
              rgba(140, 111, 61, 0.9)
            )`,
          }}
        >
          {/* Texture overlay for ink effect */}
          <div
            className="absolute inset-0 opacity-20"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='20' height='20' viewBox='0 0 20 20' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23000000' fill-opacity='0.2' fill-rule='evenodd'%3E%3Ccircle cx='3' cy='3' r='2'/%3E%3Ccircle cx='13' cy='13' r='2'/%3E%3C/g%3E%3C/svg%3E")`,
            }}
          />
        </div>

        {/* Percentage text overlay */}
        {percentage > 10 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xs font-serif font-semibold text-parchment-50 drop-shadow-sm">
              {percentage}%
            </span>
          </div>
        )}
      </div>

      <p className="text-xs text-sepia-600 mt-2 text-center italic">
        Based on strength and agreement of historical signals
      </p>
    </div>
  );
}
