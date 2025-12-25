interface DateEstimatePanelProps {
  dateRange: [number, number];
  mostLikelyYear: number;
}

export function DateEstimatePanel({ dateRange, mostLikelyYear }: DateEstimatePanelProps) {
  const [start, end] = dateRange;
  const rangeWidth = end - start;

  return (
    <div className="relative bg-parchment-100 border-4 border-double border-sepia-500 rounded-lg p-8 shadow-paper-lg">
      {/* Decorative corner flourishes */}
      <div className="absolute top-2 left-2 w-8 h-8 border-t-2 border-l-2 border-sepia-400 rounded-tl"></div>
      <div className="absolute top-2 right-2 w-8 h-8 border-t-2 border-r-2 border-sepia-400 rounded-tr"></div>
      <div className="absolute bottom-2 left-2 w-8 h-8 border-b-2 border-l-2 border-sepia-400 rounded-bl"></div>
      <div className="absolute bottom-2 right-2 w-8 h-8 border-b-2 border-r-2 border-sepia-400 rounded-br"></div>

      <div className="text-center space-y-4">
        {/* Label */}
        <div className="text-sm font-serif text-sepia-700 uppercase tracking-wider">
          Estimated Date of Creation
        </div>

        {/* Main date range */}
        <div className="space-y-2">
          {rangeWidth === 0 ? (
            <div className="text-6xl font-display font-bold text-ink">{start}</div>
          ) : (
            <div className="flex items-center justify-center space-x-3">
              <span className="text-5xl font-display font-bold text-ink">{start}</span>
              <span className="text-3xl text-sepia-600">—</span>
              <span className="text-5xl font-display font-bold text-ink">{end}</span>
            </div>
          )}

          {/* Most likely year indicator */}
          {rangeWidth > 0 && (
            <div className="text-lg font-serif text-sepia-700">
              Most likely: <span className="font-semibold text-ink">{mostLikelyYear}</span>
            </div>
          )}
        </div>

        {/* Range width info */}
        {rangeWidth > 0 && (
          <div className="text-sm text-sepia-600 italic">
            ±{rangeWidth} year{rangeWidth !== 1 ? 's' : ''} range
          </div>
        )}

        {/* Decorative divider */}
        <div className="flex items-center justify-center space-x-2 pt-2">
          <div className="h-px w-16 bg-sepia-300"></div>
          <svg className="w-4 h-4 text-sepia-400" fill="currentColor" viewBox="0 0 20 20">
            <circle cx="10" cy="10" r="3" />
          </svg>
          <div className="h-px w-16 bg-sepia-300"></div>
        </div>
      </div>
    </div>
  );
}
