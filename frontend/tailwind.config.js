/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#050505",
        foreground: "#ffffff",
        card: {
          DEFAULT: "rgba(255, 255, 255, 0.03)",
          foreground: "#ffffff",
        },
        primary: {
          DEFAULT: "#ffffff",
          foreground: "#050505",
        },
        muted: {
          DEFAULT: "rgba(255, 255, 255, 0.1)",
          foreground: "rgba(255, 255, 255, 0.6)",
        },
        accent: {
          DEFAULT: "rgba(255, 255, 255, 0.05)",
          foreground: "#ffffff",
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'glass': 'linear-gradient(180deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%)',
      },
    },
  },
  plugins: [],
}
