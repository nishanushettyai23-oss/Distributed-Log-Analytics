/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#101828",
        cloud: "#f2f4f7",
        signal: "#2563eb",
        cyan: "#0891b2",
        emerald: "#059669",
        amber: "#d97706",
        danger: "#dc2626"
      },
      boxShadow: {
        panel: "0 14px 40px rgba(16, 24, 40, 0.08)"
      }
    }
  },
  plugins: []
};
