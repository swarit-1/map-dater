/**
 * Centralized theme configuration for the Map Dater application
 * Rustic cartographer's workshop aesthetic
 */

export const theme = {
  colors: {
    // Parchment backgrounds
    parchment: {
      light: '#faf8f3',
      DEFAULT: '#f4ecd8',
      dark: '#e8d7b5',
    },
    // Sepia/brown tones
    sepia: {
      light: '#dcc9a8',
      DEFAULT: '#8c6f3d',
      dark: '#4e3f24',
    },
    // Ink colors for text
    ink: {
      DEFAULT: '#1a1a1a',
      light: '#4a4a4a',
    },
    // Accent colors
    accent: {
      red: '#8b4513', // Saddle brown for warnings
      green: '#556b2f', // Dark olive green for success
      blue: '#4682b4', // Steel blue for info
    },
  },

  fonts: {
    display: '"Playfair Display", Georgia, serif',
    serif: 'Merriweather, Georgia, serif',
    sans: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
  },

  borders: {
    thin: '1px solid #8c6f3d',
    medium: '2px solid #8c6f3d',
    decorative: '3px double #8c6f3d',
  },

  shadows: {
    paper: '0 2px 4px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)',
    paperLg: '0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)',
    emboss: 'inset 0 1px 2px rgba(255, 255, 255, 0.4), inset 0 -1px 2px rgba(0, 0, 0, 0.1)',
  },

  borderRadius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
  },
} as const;

export type Theme = typeof theme;
