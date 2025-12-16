import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Design System Colors - Deep Crimson Luxury Theme
        crimson: {
          900: '#3b0505', // Very dark shading for gradients
          800: '#610a0a', // Base deep blood red
          700: '#821e1e', // Lighter for hover states
        },
        // Backgrounds
        obsidian: '#050505', // Deepest black
        charcoal: '#0F0F0F', // Card background
        // Text
        ivory: '#F5F5F5',
        mist: '#A3A3A3',
        // Keep stage colors for architecture diagram
        sky: {
          800: '#075985', // Stage 1 color
        },
        blue: {
          800: '#1E40AF', // Stage 4 color
        },
        gray: {
          900: '#1F2937', // Headings
          600: '#4B5563', // Body
          400: '#9CA3AF', // Caption/Disabled
          50: '#F8FAFC', // Background Base
        },
        'primary-crimson': '#610a0a',
        'accent-crimson': '#821e1e',
        'text-dark': '#1F2937',
        // Stage colors for consistency
        'stage-1': '#075985', // sky-800
        'stage-2': '#610a0a', // crimson-800 (replacing violet)
        'stage-3': '#821e1e', // crimson-700 (replacing pink)
        'stage-4': '#1E40AF', // blue-800
      },
      fontFamily: {
        sans: ['Inter', 'SF Pro Display', 'system-ui', 'sans-serif'],
        serif: ['Georgia', 'Cambria', 'Times New Roman', 'Times', 'serif'],
      },
      backgroundImage: {
        'concierge-gradient': 'linear-gradient(135deg, #610a0a 0%, #821e1e 100%)',
        'crimson-gradient': 'linear-gradient(135deg, #610a0a 0%, #821e1e 100%)',
        'subtle-glow-gradient': 'linear-gradient(135deg, rgba(97, 10, 10, 0.15) 0%, rgba(130, 30, 30, 0.15) 100%)',
        'glass-gradient': 'linear-gradient(180deg, rgba(255,255,255,0.7) 0%, rgba(255,255,255,0.4) 100%)',
        'noise': "url('/noise.png')",
        'gradient-radial': 'radial-gradient(ellipse at center, var(--tw-gradient-stops))',
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(31, 38, 135, 0.05)', // Level 1
        'glass-floater': '0 10px 40px -10px rgba(97, 10, 10, 0.2)', // Level 2 - Crimson
        'glass-hover': '0 20px 40px -5px rgba(0,0,0,0.1)',
        'glow': '0 0 20px rgba(97, 10, 10, 0.4)', // Crimson glow
        'crimson-deep': '0 4px 20px rgba(97, 10, 10, 0.4)',
      },
      backdropBlur: {
        xs: '2px',
        glass: '16px', // Level 1
        floater: '24px', // Level 2
      },
      animation: {
        'gradient-shift': 'gradient-shift 8s ease infinite',
        'float': 'float 6s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'glass-appear': 'glass-appear 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55)',
        'blob': 'blob 7s infinite',
        aurora: "aurora 60s linear infinite",
        "shimmer-slide": "shimmer-slide var(--speed) ease-in-out infinite alternate",
        "spin-around": "spin-around calc(var(--speed) * 2) infinite linear",
      },
    },
  },
  plugins: [],
};

export default config;
