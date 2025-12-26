interface GameMapFrameProps {
  description: string;
  difficulty: 'beginner' | 'intermediate' | 'expert';
  mapImage?: string | null;  // Base64 encoded SVG image
}

export function GameMapFrame({ description, difficulty, mapImage }: GameMapFrameProps) {
  const getDifficultyBadge = (level: string) => {
    switch (level) {
      case 'beginner':
        return 'bg-green-100 border-green-600 text-green-800';
      case 'intermediate':
        return 'bg-blue-100 border-blue-600 text-blue-800';
      case 'expert':
        return 'bg-red-100 border-red-600 text-red-800';
      default:
        return 'bg-gray-100 border-gray-600 text-gray-800';
    }
  };

  // Decode base64 SVG to display
  const getMapImageSrc = () => {
    if (!mapImage) return null;
    // Check if it's SVG (starts with the XML declaration or <svg)
    try {
      const decoded = atob(mapImage);
      if (decoded.includes('<svg') || decoded.includes('<?xml')) {
        return `data:image/svg+xml;base64,${mapImage}`;
      }
      // Assume PNG otherwise
      return `data:image/png;base64,${mapImage}`;
    } catch {
      return `data:image/svg+xml;base64,${mapImage}`;
    }
  };

  const imageSrc = getMapImageSrc();

  return (
    <div className="w-full max-w-3xl mx-auto">
      {/* Difficulty badge */}
      <div className="flex justify-between items-center mb-4">
        <span
          className={`
          inline-block px-3 py-1 rounded-full border text-xs font-serif font-semibold uppercase tracking-wide
          ${getDifficultyBadge(difficulty)}
        `}
        >
          {difficulty}
        </span>
      </div>

      {/* Map frame with ornate border */}
      <div className="relative bg-parchment-50 border-8 border-double border-sepia-600 rounded-lg p-6 shadow-paper-lg">
        {/* Decorative corners */}
        <div className="absolute -top-3 -left-3 w-6 h-6 bg-sepia-700 rotate-45"></div>
        <div className="absolute -top-3 -right-3 w-6 h-6 bg-sepia-700 rotate-45"></div>
        <div className="absolute -bottom-3 -left-3 w-6 h-6 bg-sepia-700 rotate-45"></div>
        <div className="absolute -bottom-3 -right-3 w-6 h-6 bg-sepia-700 rotate-45"></div>

        {/* Map display area */}
        <div className="relative aspect-[4/3] bg-parchment-200 rounded border-2 border-sepia-400 overflow-hidden">
          {imageSrc ? (
            /* Actual map image */
            <img
              src={imageSrc}
              alt="Historical Map"
              className="w-full h-full object-contain"
            />
          ) : (
            /* Placeholder when no image available */
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center p-8">
                <svg
                  className="w-32 h-32 mx-auto text-sepia-300 mb-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1}
                    d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7"
                  />
                </svg>
                <p className="text-sm font-serif text-sepia-600 italic">[Loading Map...]</p>
                <p className="text-xs text-sepia-500 mt-2">{description}</p>
              </div>
            </div>
          )}

          {/* Paper texture overlay */}
          <div
            className="absolute inset-0 opacity-10 pointer-events-none"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%238c6f3d' fill-opacity='0.15'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
            }}
          />
        </div>

        {/* Map description */}
        <div className="mt-4 text-center">
          <p className="text-sm font-serif text-ink-light italic">{description}</p>
        </div>
      </div>

      {/* Instruction text */}
      <div className="mt-4 text-center text-sm text-sepia-600">
        Examine the map carefully and make your best guess about when it was created
      </div>
    </div>
  );
}
