import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: {
          950: "#07080C",
          900: "#0A0C11",
          850: "#0E1117",
          800: "#12151D",
          700: "#1A1E28",
          600: "#232834",
        },
        mist: {
          100: "#F4F6FA",
          300: "#C3C9D6",
          500: "#8A93A6",
          600: "#6B7488",
        },
        accent: {
          DEFAULT: "#8B5CF6",
          soft: "#A78BFA",
          cyan: "#22D3EE",
          mint: "#34D399",
          amber: "#FBBF24",
          rose: "#FB7185",
        },
      },
      fontFamily: {
        sans: [
          "Inter var",
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "Helvetica Neue",
          "Arial",
          "sans-serif",
        ],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "Consolas", "monospace"],
      },
      borderRadius: { xl: "14px", "2xl": "18px", "3xl": "24px" },
      boxShadow: {
        card: "0 1px 0 0 rgba(255,255,255,0.04) inset, 0 20px 40px -24px rgba(0,0,0,0.9)",
        glow: "0 0 0 1px rgba(139,92,246,0.35), 0 16px 40px -18px rgba(139,92,246,0.55)",
      },
      keyframes: {
        "fade-up": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        "pulse-ring": {
          "0%": { boxShadow: "0 0 0 0 rgba(139,92,246,0.45)" },
          "70%": { boxShadow: "0 0 0 12px rgba(139,92,246,0)" },
          "100%": { boxShadow: "0 0 0 0 rgba(139,92,246,0)" },
        },
      },
      animation: {
        "fade-up": "fade-up 0.45s cubic-bezier(0.2,0.8,0.2,1) both",
        shimmer: "shimmer 1.8s linear infinite",
        "pulse-ring": "pulse-ring 1.8s ease-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
