# Map Dater - Frontend

A React + TypeScript application for dating historical maps using computer vision and historical entity recognition. This frontend provides an intuitive interface styled as a rustic cartographer's workshop.

## Overview

Map Dater allows users to:
- **Analyze Maps**: Upload historical map images and receive date estimates based on cartographic features and historical entities
- **Play the Game**: Test knowledge of historical cartography by guessing when maps were created
- **Learn**: View detailed explanations of temporal clues and historical evidence

## Tech Stack

- **React 18** with TypeScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling with custom parchment/sepia theme
- **React Router** - Client-side routing
- **Google Fonts** - Playfair Display (headings) and Merriweather (body)

## Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The application will be available at `http://localhost:5173`

## Project Structure

```
map-dater-frontend/
├── public/              # Static assets
├── src/
│   ├── api/            # API integration layer
│   │   └── mapDaterApi.ts    # Mock API calls (replace with real endpoints)
│   ├── components/     # Reusable UI components
│   │   ├── ConfidenceBar.tsx      # Ink wash confidence visualization
│   │   ├── DateEstimatePanel.tsx  # Date range display
│   │   ├── EvidenceCard.tsx       # Historical evidence item
│   │   ├── FeedbackPanel.tsx      # Game feedback display
│   │   ├── GameMapFrame.tsx       # Map display with difficulty badge
│   │   ├── MapUploadPanel.tsx     # Drag-drop upload interface
│   │   └── ScoreSeal.tsx          # Wax seal score display
│   ├── pages/          # Top-level page components
│   │   ├── Home.tsx         # Landing page with compass rose
│   │   ├── Analyze.tsx      # Map analysis workflow
│   │   └── Game.tsx         # Interactive guessing game
│   ├── App.tsx         # Main app with routing
│   ├── main.tsx        # Entry point
│   └── index.css       # Global styles and Tailwind directives
├── tailwind.config.js  # Custom theme configuration
├── tsconfig.json       # TypeScript configuration
└── vite.config.ts      # Vite configuration
```

## Design Philosophy

The UI is designed to evoke a **rustic cartographer's workshop** aesthetic:

### Color Palette
- **Parchment** (#f4ecd8) - Warm, aged paper backgrounds
- **Sepia** (#8c6f3d) - Earthy brown for borders and accents
- **Ink** (#1a1a1a) - Deep black-brown for text

### Typography
- **Playfair Display** - Elegant serif for headings (font-display)
- **Merriweather** - Readable serif for body text (font-serif)

### Visual Elements
- Paper texture overlays (SVG patterns)
- Hand-drawn style borders
- Compass rose decorations
- Wax seal score displays
- Ink wash confidence bars

### Design Constraints
- ✅ Rustic, historical aesthetic
- ✅ Subtle animations (fade-in only)
- ❌ NO dark mode
- ❌ NO fantasy/gothic fonts
- ❌ NO excessive animations

## Components

### Analysis Components

**`MapUploadPanel`**
- Drag-and-drop file upload
- Image preview
- Loading state during analysis
- Props: `onFileSelect: (file: File) => void`, `isAnalyzing: boolean`

**`DateEstimatePanel`**
- Displays estimated date range
- Shows most likely year with decorative styling
- Props: `dateRange: [number, number]`, `mostLikelyYear: number`

**`ConfidenceBar`**
- Ink wash style confidence visualization
- Color-coded confidence levels (low/medium/high)
- Props: `confidence: number` (0-100)

**`EvidenceCard`**
- Displays individual historical evidence
- Shows entity name, validity period, and reasoning
- Props: `evidence: Evidence`, `index: number`

### Game Components

**`GameMapFrame`**
- Displays map description
- Shows difficulty badge
- Decorative corner flourishes
- Props: `description: string`, `difficulty: string`

**`ScoreSeal`**
- Wax seal style score display
- Color-coded by performance
- Props: `score: number`, `wasAccurate: boolean`

**`FeedbackPanel`**
- Educational feedback after guessing
- Comparison of user guess vs system estimate
- Detailed explanation of results
- Props: `feedback: string`, `systemEstimate: [number, number]`, `userGuess: number | [number, number]`

## API Integration

### Current State (Mock)

All API calls in `src/api/mapDaterApi.ts` are currently mocked:

```typescript
// Mock implementation with simulated delay
export async function analyzeMap(file: File): Promise<DateEstimateResponse> {
  await new Promise(resolve => setTimeout(resolve, 2000));
  return mockAnalyzeResponse;
}
```

### Connecting to Real Backend

To connect to the actual Python backend:

1. **Update base URL** in `mapDaterApi.ts`:
```typescript
const API_BASE_URL = 'http://localhost:8000'; // Your backend URL
```

2. **Replace mock functions** with real fetch calls:
```typescript
export async function analyzeMap(file: File): Promise<DateEstimateResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Failed to analyze map');
  }

  return response.json();
}
```

3. **Handle CORS** - Ensure your backend allows requests from the frontend origin:
```python
# In your FastAPI backend
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Endpoints

Expected backend endpoints:

- `POST /analyze` - Upload and analyze a map image
  - Request: `multipart/form-data` with `file` field
  - Response: `DateEstimateResponse`

- `POST /game/start` - Start a new game round
  - Request: `{ difficulty: 'beginner' | 'intermediate' | 'expert' }`
  - Response: `GameRoundResponse`

- `POST /game/submit` - Submit a guess
  - Request: `{ round_id: string, guess: number | [number, number] }`
  - Response: `GameResultResponse`

## Customization

### Theme Colors

Edit `tailwind.config.js` to modify the color palette:

```javascript
theme: {
  extend: {
    colors: {
      parchment: {
        50: '#faf8f3',   // Lightest
        100: '#f4ecd8',  // Main background
        // ... add more shades
      },
      sepia: {
        // Brown tones for accents
      }
    }
  }
}
```

### Typography

Change fonts in `src/index.css`:

```css
@import url('https://fonts.googleapis.com/css2?family=YourFont:wght@400;700&display=swap');
```

Then update `tailwind.config.js`:

```javascript
fontFamily: {
  serif: ['YourFont', 'Georgia', 'serif'],
}
```

### Paper Texture

The paper texture is defined in `src/index.css` as a CSS utility class:

```css
.paper-texture::before {
  background-image: url("data:image/svg+xml,...");
  opacity: 0.3; /* Adjust texture visibility */
}
```

## Development

### Running Tests

```bash
# Tests not yet implemented
npm run test
```

### Linting

```bash
npm run lint
```

### Type Checking

```bash
npx tsc --noEmit
```

## Build and Deployment

### Production Build

```bash
npm run build
```

Build output will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

### Deployment Options

The built application is a static site and can be deployed to:
- **Vercel**: `npx vercel`
- **Netlify**: Drag `dist/` folder to Netlify
- **GitHub Pages**: Use `gh-pages` package
- **Static hosting**: Upload `dist/` contents

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Performance Considerations

- Images are not optimized in the mock version
- Consider adding lazy loading for production
- Large uploaded images should be compressed before upload
- Add loading skeletons for better UX during analysis

## Future Enhancements

Potential features not yet implemented:
- User authentication and saved analyses
- History of analyzed maps
- Social sharing of game scores
- Advanced filtering in evidence view
- Comparison mode (multiple maps side-by-side)
- Export analysis reports as PDF

## License

This project is part of the Map Dater system.

## Contributing

When contributing to the UI:
1. Follow the established design system (parchment/sepia palette)
2. Maintain the rustic aesthetic
3. Ensure TypeScript types are properly defined
4. Test on multiple screen sizes
5. Keep animations subtle and purposeful

---

Built with React, TypeScript, and Tailwind CSS. Designed to feel like a cartographer's workshop from centuries past.
