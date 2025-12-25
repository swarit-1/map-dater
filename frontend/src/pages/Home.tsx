import { Link } from 'react-router-dom';

export function Home() {
  return (
    <div className="min-h-screen bg-parchment-100 flex flex-col items-center justify-center p-6">
      {/* Decorative header with compass rose */}
      <div className="mb-8">
        <svg className="w-24 h-24 text-sepia-500 mx-auto mb-4" viewBox="0 0 100 100" fill="none">
          {/* Compass rose design */}
          <circle cx="50" cy="50" r="45" stroke="currentColor" strokeWidth="2" fill="none" />
          <circle cx="50" cy="50" r="35" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.5" />

          {/* North pointer */}
          <path d="M50 10 L55 40 L50 35 L45 40 Z" fill="currentColor" />

          {/* Cardinal directions */}
          <path d="M50 90 L55 60 L50 65 L45 60 Z" fill="currentColor" opacity="0.7" />
          <path d="M10 50 L40 45 L35 50 L40 55 Z" fill="currentColor" opacity="0.7" />
          <path d="M90 50 L60 45 L65 50 L60 55 Z" fill="currentColor" opacity="0.7" />

          {/* Intercardinal lines */}
          <line x1="50" y1="15" x2="50" y2="85" stroke="currentColor" strokeWidth="1" opacity="0.3" />
          <line x1="15" y1="50" x2="85" y2="50" stroke="currentColor" strokeWidth="1" opacity="0.3" />

          {/* Center decoration */}
          <circle cx="50" cy="50" r="5" fill="currentColor" />

          {/* N marker */}
          <text x="50" y="8" textAnchor="middle" fontSize="8" fill="currentColor" fontFamily="serif" fontWeight="bold">
            N
          </text>
        </svg>
      </div>

      {/* Title section */}
      <div className="text-center mb-12 max-w-2xl">
        <h1 className="text-6xl font-display font-bold text-ink mb-4">Map Dater</h1>

        {/* Decorative line */}
        <div className="flex items-center justify-center space-x-3 mb-6">
          <div className="h-px w-24 bg-sepia-400"></div>
          <svg className="w-4 h-4 text-sepia-500" fill="currentColor" viewBox="0 0 20 20">
            <circle cx="10" cy="10" r="3" />
          </svg>
          <div className="h-px w-24 bg-sepia-400"></div>
        </div>

        <p className="text-xl font-serif text-ink-light leading-relaxed">
          Estimate when a map was created using historical clues
        </p>

        <p className="mt-4 text-sm text-sepia-600 max-w-lg mx-auto">
          Our system analyzes cartographic features, political entities, and place names to determine the approximate
          era of creation for historical maps.
        </p>
      </div>

      {/* Action buttons */}
      <div className="flex flex-col sm:flex-row gap-6 mb-12">
        <Link
          to="/analyze"
          className="group relative px-8 py-4 bg-sepia-600 text-parchment-50 font-serif font-semibold text-lg rounded-lg shadow-paper hover:shadow-paper-lg transition-all duration-200 hover:bg-sepia-700"
        >
          <div className="flex items-center space-x-3">
            <svg
              className="w-6 h-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <span>Analyze a Map</span>
          </div>

          {/* Decorative corner */}
          <div className="absolute top-1 right-1 w-3 h-3 border-t-2 border-r-2 border-parchment-200 opacity-50 rounded-tr"></div>
        </Link>

        <Link
          to="/game"
          className="group relative px-8 py-4 bg-parchment-50 text-sepia-700 border-2 border-sepia-500 font-serif font-semibold text-lg rounded-lg shadow-paper hover:shadow-paper-lg transition-all duration-200 hover:bg-parchment-200"
        >
          <div className="flex items-center space-x-3">
            <svg
              className="w-6 h-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
              />
            </svg>
            <span>Play the Map Dating Game</span>
          </div>

          {/* Decorative corner */}
          <div className="absolute top-1 right-1 w-3 h-3 border-t-2 border-r-2 border-sepia-500 opacity-50 rounded-tr"></div>
        </Link>
      </div>

      {/* Footer info */}
      <div className="mt-8 text-center text-sm text-sepia-600 max-w-md">
        <p className="italic">
          Built for historians, cartographers, and map enthusiasts. Uses historical entity recognition and temporal
          analysis.
        </p>
      </div>
    </div>
  );
}
