import { Evidence } from '../api/mapDaterApi';

interface EvidenceCardProps {
  evidence: Evidence;
  index: number;
}

export function EvidenceCard({ evidence, index }: EvidenceCardProps) {
  const { label, valid_range, explanation } = evidence;

  return (
    <div className="bg-parchment-100 border-l-4 border-sepia-500 rounded-r p-4 shadow-paper hover:shadow-paper-lg transition-shadow duration-200">
      <div className="flex items-start space-x-3">
        {/* Index number in decorative circle */}
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-sepia-600 text-parchment-50 flex items-center justify-center font-serif font-bold text-sm shadow-sm">
          {index}
        </div>

        <div className="flex-1">
          {/* Signal label */}
          <h4 className="font-serif font-semibold text-ink text-base mb-1">{label}</h4>

          {/* Valid range */}
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-xs font-serif text-sepia-700 bg-sepia-100 px-2 py-1 rounded border border-sepia-300">
              Valid {valid_range[0]}–{valid_range[1]}
            </span>
          </div>

          {/* Explanation */}
          <p className="text-sm text-ink-light leading-relaxed">{explanation}</p>
        </div>
      </div>

      {/* Decorative corner element */}
      <svg
        className="absolute top-0 right-0 w-6 h-6 text-sepia-200 opacity-30"
        viewBox="0 0 24 24"
        fill="currentColor"
      >
        <path d="M0 0h24v24H0V0z" fill="none" />
        <path d="M12 2l-5.5 9h11z" />
      </svg>
    </div>
  );
}
