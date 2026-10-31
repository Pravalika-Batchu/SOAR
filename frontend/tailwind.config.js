/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        soc: {
          bg: "#0B0F17",
          card: "#111827",
          cardHover: "#1E293B",
          border: "#1F2937",
          primary: "#3B82F6",
          accent: "#06B6D4",
          success: "#10B981",
          warning: "#F59E0B",
          danger: "#EF4444",
          muted: "#9CA3AF"
        }
      }
    },
  },
  plugins: [],
}

