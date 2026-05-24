/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        charcoal: '#121212',
        charcoalLight: '#1e1e1e',
        neonCyan: '#00f3ff',
        neonBlue: '#0055ff',
        alertRed: '#ff003c',
        alertOrange: '#ff8c00',
        alertYellow: '#ffd700',
        safeGreen: '#00ff88',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
