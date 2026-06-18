/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#020617',   // True OLED black
        surface: '#0F172A',      // Slate 900
        surfaceHigh: '#1E293B',  // Slate 800
        brand: '#6366f1',        // Indigo 500
        brandLight: '#818cf8',   // Indigo 400
        brandDim: '#4f46e5',     // Indigo 600
        violet: '#8b5cf6',       // Violet 500
        success: '#10b981',      // Emerald 500
        danger: '#ef4444',       // Red 500
        warning: '#f59e0b',      // Amber 500
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
        display: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
      },
      animation: {
        blob: "blob 7s infinite",
        shimmer: "shimmer 2s linear infinite",
        'fade-in': "fadeIn 0.6s ease-out forwards",
        'slide-up': "slideUp 0.5s ease-out forwards",
        'glow-pulse': "glowPulse 3s ease-in-out infinite",
      },
      keyframes: {
        blob: {
          "0%": { transform: "translate(0px, 0px) scale(1)" },
          "33%": { transform: "translate(30px, -50px) scale(1.1)" },
          "66%": { transform: "translate(-20px, 20px) scale(0.9)" },
          "100%": { transform: "translate(0px, 0px) scale(1)" },
        },
        shimmer: {
          from: { backgroundPosition: "0 0" },
          to: { backgroundPosition: "-200% 0" },
        },
        fadeIn: {
          from: { opacity: "0" },
          to: { opacity: "1" },
        },
        slideUp: {
          from: { opacity: "0", transform: "translateY(20px)" },
          to: { opacity: "1", transform: "translateY(0)" },
        },
        glowPulse: {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "0.9" },
        },
      },
      boxShadow: {
        'brand': '0 0 30px rgba(99, 102, 241, 0.25)',
        'brand-sm': '0 0 12px rgba(99, 102, 241, 0.15)',
        'brand-lg': '0 0 60px rgba(99, 102, 241, 0.35)',
        'violet': '0 0 30px rgba(139, 92, 246, 0.25)',
        'success-glow': '0 0 20px rgba(16, 185, 129, 0.2)',
        'glass': '0 8px 32px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.06)',
        'card': '0 4px 24px rgba(0, 0, 0, 0.35)',
        'card-hover': '0 8px 40px rgba(0, 0, 0, 0.5)',
      },
      backgroundImage: {
        'gradient-brand': 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
        'gradient-brand-soft': 'linear-gradient(135deg, rgba(99,102,241,0.12) 0%, rgba(139,92,246,0.12) 100%)',
        'gradient-glass': 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%)',
        'gradient-surface': 'linear-gradient(180deg, rgba(15,23,42,0.95) 0%, rgba(2,6,23,0.95) 100%)',
      },
    },
  },
  plugins: [],
}
