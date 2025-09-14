/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // SketchFlow Gentle Color Palette
      colors: {
        // Deep Navy Blue - Primary brand color
        navy: {
          50: '#f0f4f8',
          100: '#d9e2ec',
          200: '#bcccdc',
          300: '#9fb3c8',
          400: '#829ab1',
          500: '#627d98',
          600: '#486581',
          700: '#334e68',
          800: '#243b53',
          900: '#0d3b66', // Main navy
          950: '#102a43',
        },
        // Warm Cream - Gentle backgrounds
        cream: {
          50: '#fefdfb',
          100: '#fefcf6',
          200: '#fcf7e9',
          300: '#faf0ca', // Main cream
          400: '#f7e6a3',
          500: '#f4dc7c',
          600: '#f0d155',
          700: '#e6c547',
          800: '#d4b63a',
          900: '#c2a72d',
        },
        // Golden Yellow - Bright optimistic
        golden: {
          50: '#fefcf0',
          100: '#fef9e0',
          200: '#fef2c2',
          300: '#fde895',
          400: '#fcdd67',
          500: '#f4d35e', // Main golden
          600: '#e6c054',
          700: '#d4a649',
          800: '#c2933f',
          900: '#b08035',
        },
        // Warm Orange - Energetic friendly
        orange: {
          50: '#fef7f0',
          100: '#feedde',
          200: '#fdd9bd',
          300: '#fcc49c',
          400: '#fbaf7b',
          500: '#ee964b', // Main orange
          600: '#e58643',
          700: '#d7763a',
          800: '#c96632',
          900: '#bb562a',
        },
        // Coral Red - Vibrant attention
        coral: {
          50: '#fef6f4',
          100: '#fee9e5',
          200: '#fdd3cb',
          300: '#fcb8a8',
          400: '#fa9d85',
          500: '#f95738', // Main coral
          600: '#f04e32',
          700: '#e7452c',
          800: '#de3c26',
          900: '#d53320',
        },
        // Neutral tones derived from the palette
        neutral: {
          50: '#faf9f7',
          100: '#f2f0ec',
          200: '#e8e4dd',
          300: '#d6d0c4',
          400: '#b8ae9d',
          500: '#9a8c75',
          600: '#7c6b55',
          700: '#5e5242',
          800: '#423a32',
          900: '#2d2622',
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