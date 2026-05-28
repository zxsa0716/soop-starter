'use client';

import { useState } from 'react';
import ChatStream from '@/components/ChatStream';
import PersonaCards from '@/components/PersonaCards';

export default function HomePage() {
  const [activePersona, setActivePersona] = useState<string | null>(null);

  return (
    <main className="min-h-screen px-6 py-10 max-w-6xl mx-auto">
      {/* Hero */}
      <header className="mb-10 border-b-4 border-forest-deep pb-8">
        <p className="text-xs tracking-[0.3em] text-bark mb-2">TR-2026-001 · SOOP STARTER</p>
        <h1 className="font-serif text-5xl md:text-7xl font-black leading-tight">
          숲스타터 <span className="text-forest-deep">Soop Starter</span>
        </h1>
        <p className="mt-4 font-serif italic text-bark max-w-2xl text-lg">
          한국 산촌 청년 임업인 진입 의사결정 지원 시스템 — 자연어 인터뷰 한 번으로
          마을·임산물·쉼터·5년 소득·보조사업·멘토 6가지 통합 결정 패키지.
        </p>
        <p className="mt-3 text-xs font-mono text-stone-500">
          88팀 중 4개 주관기관 데이터를 모두 활용하는 첫 작품 · 본선 발표 2026.07.21~22
        </p>
      </header>

      {/* 4 페르소나 */}
      <section className="mb-12">
        <h2 className="font-serif text-2xl font-bold mb-4 text-forest-deep">
          4 페르소나 시연
        </h2>
        <PersonaCards onSelect={setActivePersona} active={activePersona} />
      </section>

      {/* Chat */}
      <section className="mb-12">
        <h2 className="font-serif text-2xl font-bold mb-4 text-forest-deep">
          자연어 인터뷰
        </h2>
        <ChatStream personaSeed={activePersona} />
      </section>

      <footer className="text-xs text-stone-500 font-mono text-center mt-16 pb-10">
        Soop Starter · MIT License · 2026
      </footer>
    </main>
  );
}
