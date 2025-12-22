interface ScoreSealProps {
  score: number; // 0-100
  wasAccurate: boolean;
}

export function ScoreSeal({ score, wasAccurate }: ScoreSealProps) {
  const getScoreLabel = (s: number): string => {
    if (s >= 90) return 'Excellent';
    if (s >= 75) return 'Very Good';
    if (s >= 60) return 'Good';
    if (s >= 40) return 'Fair';
    return 'Try Again';
  };

  const getScoreColor = (s: number): string => {
    if (s >= 75) return 'text-accent-green';
    if (s >= 50) return 'text-accent-blue';
    return 'text-accent-red';
  };

  const getSealColor = (s: number): string => {
    if (s >= 75) return '#556b2f'; // Dark olive green
    if (s >= 50) return '#4682b4'; // Steel blue
    return '#8b4513'; // Saddle brown
  };

  return (
    <div className="flex flex-col items-center">
      {/* Wax seal effect */}
      <div className="relative">
        {/* Outer seal */}
        <svg className="w-32 h-32" viewBox="0 0 100 100">
          {/* Seal background */}
          <circle cx="50" cy="50" r="45" fill={getSealColor(score)} opacity="0.9" />

          {/* Seal edge texture */}
          <circle cx="50" cy="50" r="45" fill="none" stroke={getSealColor(score)} strokeWidth="2" />

          {/* Inner decorative circle */}
          <circle cx="50" cy="50" r="38" fill="none" stroke="#f4ecd8" strokeWidth="1.5" strokeDasharray="3,2" opacity="0.6" />

          {/* Score text */}
          <text x="50" y="45" textAnchor="middle" className="fill-parchment-50" fontSize="24" fontWeight="bold" fontFamily="serif">
            {score}
          </text>

          {/* Out of 100 */}
          <text x="50" y="62" textAnchor="middle" className="fill-parchment-100" fontSize="10" fontFamily="serif" opacity="0.8">
            / 100
          </text>
        </svg>

        {/* Ribbon decoration */}
        <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 flex space-x-1">
          <div
            className="w-12 h-3 rounded-b"
            style={{
              backgroundColor: getSealColor(score),
              opacity: 0.8,
              clipPath: 'polygon(0 0, 100% 0, 90% 100%, 10% 100%)',
            }}
          />
        </div>
      </div>

      {/* Score label */}
      <div className={`mt-6 text-2xl font-display font-bold ${getScoreColor(score)}`}>
        {getScoreLabel(score)}
      </div>

      {/* Accuracy indicator */}
      <div className="mt-2 text-sm font-serif">
        {wasAccurate ? (
          <span className="text-accent-green">✓ Your guess overlapped with the actual range</span>
        ) : (
          <span className="text-accent-red">✗ Your guess missed the actual range</span>
        )}
      </div>

      {/* Decorative divider */}
      <div className="mt-4 flex items-center space-x-2">
        <div className="h-px w-8 bg-sepia-400"></div>
        <svg className="w-3 h-3 text-sepia-500" fill="currentColor" viewBox="0 0 20 20">
          <path d="M10 2a1 1 0 011 1v1.323l3.954 1.582 1.599-.8a1 1 0 01.894 1.79l-1.233.616 1.738 5.42a1 1 0 01-.285 1.05A3.989 3.989 0 0115 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.715-5.349L11 6.477V16h2a1 1 0 110 2H7a1 1 0 110-2h2V6.477L6.237 7.582l1.715 5.349a1 1 0 01-.285 1.05A3.989 3.989 0 015 15a3.989 3.989 0 01-2.667-1.019 1 1 0 01-.285-1.05l1.738-5.42-1.233-.617a1 1 0 01.894-1.788l1.599.799L9 4.323V3a1 1 0 011-1z" />
        </svg>
        <div className="h-px w-8 bg-sepia-400"></div>
      </div>
    </div>
  );
}
