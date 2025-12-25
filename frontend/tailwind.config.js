/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        parchment: {
          50: '#faf8f3',
          100: '#f4ecd8',
          200: '#e8d7b5',
          300: '#dbc192',
          400: '#ceab6f',
          500: '#c1954c',
          600: '#9a7740',
          700: '#735934',
          800: '#4d3b23',
          900: '#261d11',
        },
        sepia: {
          50: '#faf6f1',
          100: '#f0e6d6',
          200: '#dcc9a8',
          300: '#c8ac7a',
          400: '#b48f4c',
          500: '#8c6f3d',
          600: '#6d5730',
          700: '#4e3f24',
          800: '#2f2717',
          900: '#100f0b',
        },
        ink: {
          DEFAULT: '#1a1a1a',
          light: '#4a4a4a',
        },
      },
      fontFamily: {
        serif: ['Merriweather', 'Georgia', 'serif'],
        display: ['Playfair Display', 'Georgia', 'serif'],
      },
      boxShadow: {
        'paper': '0 2px 4px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06)',
        'paper-lg': '0 4px 6px rgba(0, 0, 0, 0.1), 0 2px 4px rgba(0, 0, 0, 0.06)',
        'emboss': 'inset 0 1px 2px rgba(255, 255, 255, 0.4), inset 0 -1px 2px rgba(0, 0, 0, 0.1)',
      },
    },
  },
  plugins: [],
}
