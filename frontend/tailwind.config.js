/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // SketchFlow New Minimal Palette
      colors: {
        brand: {
          background: '#ffffff',
          surface: '#F6F5F5',
          muted: '#D3E0EA',
          primary: '#1687A7',
          secondary: '#276678',
          foreground: '#1f2937',
        },
        // Semantic scales used in components
        primary: {
          50: '#EAF6FB',
          100: '#D3ECF5',
          200: '#A7D9EB',
          300: '#7BC6E1',
          400: '#4FB3D7',
          500: '#1687A7',
          600: '#126F8A',
          700: '#0E586E',
          800: '#0B4051',
          900: '#072A35',
        },
        secondary: {
          50: '#EAF2F4',
          100: '#D3E0EA',
          200: '#B6CCD7',
          300: '#8FB0BF',
          400: '#5F8E9F',
          500: '#276678',
          600: '#1F5463',
          700: '#173F4E',
          800: '#0F3039',
          900: '#0A242B',
        },
        // Keep functional colors for status UIs
        success: {
          50: '#ECFDF5',
          100: '#D1FAE5',
          200: '#A7F3D0',
          300: '#6EE7B7',
          400: '#34D399',
          500: '#10B981',
          600: '#059669',
          700: '#047857',
          800: '#065F46',
          900: '#064E3B',
        },
        info: {
          50: '#EFF6FF',
          100: '#DBEAFE',
          200: '#BFDBFE',
          300: '#93C5FD',
          400: '#60A5FA',
          500: '#3B82F6',
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
        },
        warning: {
          50: '#FFFBEB',
          100: '#FEF3C7',
          200: '#FDE68A',
          300: '#FCD34D',
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
          700: '#B45309',
          800: '#92400E',
          900: '#78350F',
        },
        error: {
          50: '#FEF2F2',
          100: '#FEE2E2',
          200: '#FECACA',
          300: '#FCA5A5',
          400: '#F87171',
          500: '#EF4444',
          600: '#DC2626',
          700: '#B91C1C',
          800: '#991B1B',
          900: '#7F1D1D',
        },
      },
      // Typography System
      fontFamily: {
        sans: ['var(--font-inter)', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains-mono)', 'JetBrains Mono', 'Menlo', 'Monaco', 'monospace'],
      },
      fontSize: {
        'display': ['3rem', { lineHeight: '3.5rem', letterSpacing: '-0.02em' }], // 48px
        '4xl': ['2rem', { lineHeight: '2.5rem', letterSpacing: '-0.01em' }], // 32px
        '3xl': ['1.5rem', { lineHeight: '2rem' }], // 24px
        '2xl': ['1.25rem', { lineHeight: '1.75rem' }], // 20px
        'lg': ['1.125rem', { lineHeight: '1.75rem' }], // 18px
        'base': ['1rem', { lineHeight: '1.5rem' }], // 16px
        'sm': ['0.875rem', { lineHeight: '1.25rem' }], // 14px
        'xs': ['0.75rem', { lineHeight: '1rem' }], // 12px
      },
      // Spacing System (8px base)
      spacing: {
        '18': '4.5rem',
        '72': '18rem',
        '84': '21rem',
        '96': '24rem',
      },
      // Border Radius
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      // Box Shadows with elevation system
      boxShadow: {
        'elevation-1': '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        'elevation-2': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'elevation-4': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'elevation-8': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
      },
      // Animation & Transitions
      transitionDuration: {
        '400': '400ms',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
        'pulse-subtle': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      // Breakpoints (mobile-first)
      screens: {
        'xs': '320px',
        'sm': '640px',
        'md': '768px',
        'lg': '1024px',
        'xl': '1280px',
        '2xl': '1536px',
      },
    },
  },
  plugins: [],
  darkMode: 'media', // Use system preference
}
