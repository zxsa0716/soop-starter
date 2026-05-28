'use client';

import { useEffect, useRef, useState } from 'react';

interface ChatChunk {
  type: 'text' | 'tool_result' | 'done' | 'error';
  delta?: string;
  name?: string;
  module?: string;
  summary?: string;
  message?: string;
  state?: string;
}

interface Message {
  role: 'user' | 'assistant';
  text: string;
  toolCalls?: { module: string; summary: string }[];
}

const PERSONA_PROMPTS: Record<string, string> = {
  'P-01': '저는 35세 IT 직장인이고요, 자본 5천만 정도로 강원도에 가서 표고를 키우고 싶어요. 처음엔 주말농장처럼 시작해서 5년 안에 점진적으로 전환하고 싶습니다. 가족은 아내랑 둘이고, 아직 아이는 없어요.',
  'P-02': '28세 디자이너고 자본은 2천만 정도, 임업은 처음이에요. 충북 가서 산양삼 키워보고 싶고 산림조합 인턴십처럼 학습할 수 있는 곳이 좋아요.',
  'P-03': '45세 회사원입니다. 부친 임야 3ha를 진안에 상속받았어요. 5년 후 퇴직과 동시에 본격 전환할 계획이고, 표고에 KOC 등록까지 노리고 있습니다. 자본은 1.5억 정도 됩니다.',
  'P-04': '30세 IT입니다. 대구 사는데 자본 3천만으로 영양 어수리 임산물 스마트팜 임대 들어가고 싶어요. 18~40세 청년 자격 됩니다.',
};

export default function ChatStream({ personaSeed }: { personaSeed: string | null }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const wsRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const apiBase = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';
    const wsUrl = apiBase.replace(/^http/, 'ws') + '/chat';
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onmessage = (e) => {
      const chunk = JSON.parse(e.data) as ChatChunk;
      if (chunk.type === 'text') {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === 'assistant') {
            return [...prev.slice(0, -1), { ...last, text: last.text + (chunk.delta ?? '') }];
          }
          return [...prev, { role: 'assistant', text: chunk.delta ?? '' }];
        });
      } else if (chunk.type === 'tool_result') {
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          const toolCall = { module: chunk.module ?? '', summary: chunk.summary ?? '' };
          if (last?.role === 'assistant') {
            return [...prev.slice(0, -1),
              { ...last, toolCalls: [...(last.toolCalls ?? []), toolCall] }];
          }
          return [...prev, { role: 'assistant', text: '', toolCalls: [toolCall] }];
        });
      }
    };
    return () => ws.close();
  }, []);

  useEffect(() => {
    if (personaSeed && PERSONA_PROMPTS[personaSeed]) {
      setInput(PERSONA_PROMPTS[personaSeed]);
    }
  }, [personaSeed]);

  function send() {
    if (!input.trim() || !wsRef.current) return;
    setMessages((prev) => [...prev, { role: 'user', text: input }]);
    wsRef.current.send(JSON.stringify({ text: input }));
    setInput('');
  }

  return (
    <div className="border-2 border-forest-deep rounded p-6 bg-white/70 min-h-[400px]">
      <div className="flex items-center justify-between mb-4">
        <p className="text-xs font-mono text-bark">
          {connected ? '● WS 연결됨' : '○ 연결 중...'}
        </p>
        <p className="text-xs font-mono text-stone-500">latency 목표: 첫 토큰 ≤ 2초 · 전체 ≤ 15초</p>
      </div>

      <div className="space-y-4 max-h-[480px] overflow-y-auto mb-4">
        {messages.length === 0 && (
          <p className="text-stone-400 italic text-sm">
            위의 페르소나를 선택하거나 자연어로 직접 입력하세요.
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={m.role === 'user' ? 'text-right' : ''}>
            <div className={`inline-block max-w-[80%] p-3 rounded ${
              m.role === 'user'
                ? 'bg-forest-deep text-paper'
                : 'bg-paper border border-stone-300'
            }`}>
              <p className="text-xs font-mono opacity-60 mb-1">
                {m.role === 'user' ? 'USER' : 'CLAUDE OPUS 4.7'}
              </p>
              <p className="whitespace-pre-wrap leading-relaxed">{m.text}</p>
              {m.toolCalls && m.toolCalls.length > 0 && (
                <div className="mt-2 pt-2 border-t border-stone-300 space-y-1">
                  {m.toolCalls.map((tc, j) => (
                    <p key={j} className="text-xs font-mono text-ochre">
                      ▶ {tc.module} · {tc.summary}
                    </p>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="flex gap-2 border-t pt-4">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && send()}
          placeholder="자연어로 말씀해주세요. 예: 35세 IT, 강원도 표고, 5천만..."
          className="flex-1 p-3 border border-stone-400 rounded font-sans"
        />
        <button
          onClick={send}
          disabled={!connected || !input.trim()}
          className="px-6 py-3 bg-forest-deep text-paper rounded font-bold disabled:opacity-40 hover:bg-forest transition"
        >
          전송
        </button>
      </div>
    </div>
  );
}
