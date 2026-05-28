import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        forest: {
          deep: '#1F3320', DEFAULT: '#2D4A2B', soft: '#6B7E5A',
        },
        paper: '#F5EFE3',
        bark: '#3F2A1D',
        ochre: '#B8893E',
      },
      fontFamily: {
        serif: ['"Noto Serif KR"', 'serif'],
        sans: ['Pretendard', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
};
export default config;
