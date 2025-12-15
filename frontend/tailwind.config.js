/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2F5233", // Deep Green
        secondary: "#94C973", // Light Green
        accent: "#F1D302", // Yellow/Gold
        background: "#F0F7F4", // Mint Cream
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
