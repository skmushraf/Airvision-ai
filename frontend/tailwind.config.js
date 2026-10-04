/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class', // class-based dark mode (toggled by ThemeContext)
  theme: {
    extend: {
      fontFamily: {
        sans: [
          'Inter', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto',
          'Helvetica Neue', 'Arial', 'sans-serif',
        ],
      },
      colors: {
        brand: {
          50: '#eef6ff',
          100: '#d9ebff',
          200: '#bcdcff',
          300: '#8ec6ff',
          400: '#59a6ff',
          500: '#3384fb',
          600: '#1d63f0',
          700: '#154cdd',
          800: '#173eb3',
          900: '#19398d',
        },
        aqi: {
          good: '#22c55e',
          satisfactory: '#a3e635',
          moderate: '#f97316',
          poor: '#ef4444',
          verypoor: '#b91c1c',
          severe: '#a855f7',
        },
      },
      boxShadow: {
        card: '0 1px 2px rgba(15, 23, 42, 0.06), 0 8px 24px -12px rgba(15, 23, 42, 0.18)',
        'card-lg': '0 2px 4px rgba(15, 23, 42, 0.06), 0 16px 40px -16px rgba(15, 23, 42, 0.25)',
        glow: '0 0 24px -6px rgba(51, 132, 251, 0.55)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow': 'spin 2.4s linear infinite',
      },
    },
  },
  plugins: [],
}
