/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },
      colors: {
        brand: {
          teal  : '#43e8d8',
          blue  : '#4e9df5',
          purple: '#9e5ee3',
          pink  : '#f064d2',
        },
      },
      backgroundImage: {
        'auth-grad': 'linear-gradient(135deg, #43e8d8 0%, #4e9df5 35%, #9e5ee3 70%, #f064d2 100%)',
        'btn-grad' : 'linear-gradient(90deg, #00d2ff, #c471ed)',
      },
      borderRadius: {
        card: '18px',
      },
      boxShadow: {
        card: '0 24px 64px rgba(0,0,0,0.14)',
        btn : '0 4px 18px rgba(196,113,237,0.40)',
      },
      keyframes: {
        breathe: {
          '0%,100%': { transform: 'scale(1) translateY(0)' },
          '50%':     { transform: 'scale(1.03) translateY(-8px)' },
        },
        spin: {
          to: { transform: 'rotate(360deg)' },
        },
      },
      animation: {
        breathe: 'breathe 9s ease-in-out infinite',
        spin   : 'spin 0.7s linear infinite',
      },
    },
  },
  plugins: [],
};
