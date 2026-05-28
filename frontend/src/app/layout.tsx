import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '숲스타터 · Soop Starter',
  description:
    '한국 산촌 청년 임업인 진입 의사결정 지원 시스템 · 2026 산림 공공데이터·AI 활용 창업경진대회',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;700;900&display=swap"
          rel="stylesheet"
        />
        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable.min.css"
        />
      </head>
      <body className="bg-paper text-stone-900 antialiased font-sans">{children}</body>
    </html>
  );
}
