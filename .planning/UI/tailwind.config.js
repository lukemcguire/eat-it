/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3b82f6',
          synchronized: '#207fdf',
        },
        background: {
          light: '#f5f7f8',
          dark: '#0f1923',
          nordic: '#0f172a',
          charcoal: '#0b1219',
        },
        surface: {
          dark: '#1a2632',
          elevated: '#1e293b',
        },
        border: {
          dark: '#2e4e6b',
          muted: '#2d3d4d',
          subtle: '#334155',
        },
        'nordic-blue': '#a5c1d9',
        charcoal: {
          50: '#f1f5f9',
          100: '#e2e8f0',
          200: '#cbd5e1',
          300: '#94a3b8',
          400: '#64748b',
          500: '#475569',
          600: '#334155',
          700: '#1e293b',
          800: '#0f172a',
          900: '#020617',
        },
      },
      fontFamily: {
        display: ['Space Grotesk', 'Manrope', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0.5rem',
        lg: '0.75rem',
        xl: '1rem',
        '2xl': '1.5rem',
        full: '9999px',
      },
    },
  },
  plugins: [],
};
