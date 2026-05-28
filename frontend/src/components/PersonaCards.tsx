'use client';

const PERSONAS = [
  { id: 'P-01', name: '김도현 · 35 IT', cap: '5천만', region: '평창 진부', product: '표고',
    p50: '+1.2억', policy: '산촌체류형 쉼터 (2026 NEW)' },
  { id: 'P-02', name: '이수진 · 28 디자이너', cap: '2천만', region: '충주 살미', product: '산양삼',
    p50: '+4,500만', policy: '임업후계자 + 예비사회적기업' },
  { id: 'P-03', name: '박재훈 · 45 회사원', cap: '1.5억', region: '진안 (상속 3ha)', product: '표고+KOC',
    p50: '+1.8억', policy: '산림 미래혁신센터 90억 (NEW)' },
  { id: 'P-04', name: '정민호 · 30 IT', cap: '3천만', region: '영양 (임대)', product: '어수리 스마트팜',
    p50: '+2.7억', policy: '★ 영양 105억 (2026 NEW)' },
];

export default function PersonaCards({
  onSelect, active,
}: { onSelect: (id: string) => void; active: string | null }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
      {PERSONAS.map((p) => (
        <button
          key={p.id}
          onClick={() => onSelect(p.id)}
          className={`text-left p-4 border-2 rounded transition ${
            active === p.id
              ? 'border-forest-deep bg-forest-deep text-paper'
              : 'border-stone-300 bg-white/70 hover:border-forest-deep'
          }`}
        >
          <p className={`text-[10px] font-mono mb-1 ${
            active === p.id ? 'text-ochre' : 'text-bark'
          }`}>
            PERSONA {p.id}
          </p>
          <h3 className="font-serif font-bold text-base mb-2">{p.name}</h3>
          <dl className="text-xs space-y-1 font-mono">
            <div><span className="opacity-60">자본</span> {p.cap}</div>
            <div><span className="opacity-60">거점</span> {p.region}</div>
            <div><span className="opacity-60">임산물</span> {p.product}</div>
            <div className="font-bold">
              <span className="opacity-60">P50 5y</span> {p.p50}
            </div>
          </dl>
          <p className={`text-[10px] mt-2 ${
            active === p.id ? 'text-paper opacity-90' : 'text-forest-deep'
          }`}>
            {p.policy}
          </p>
        </button>
      ))}
    </div>
  );
}
