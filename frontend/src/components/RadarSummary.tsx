'use client';

import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts';

interface RadarAxes {
  forestry_fit: number;
  lifestyle: number;
  policy_match: number;
  safety: number;
}

export default function RadarSummary({ axes }: { axes: RadarAxes }) {
  const data = [
    { axis: '임업 적합', value: axes.forestry_fit * 100 },
    { axis: '라이프스타일', value: axes.lifestyle * 100 },
    { axis: '정책 매칭', value: axes.policy_match * 100 },
    { axis: '안전', value: axes.safety * 100 },
  ];
  return (
    <div className="w-full h-64 p-4 border border-stone-300 bg-white/70 rounded">
      <p className="text-xs font-mono text-bark mb-2">마을 4축 레이더 (M02 + M11)</p>
      <ResponsiveContainer width="100%" height="85%">
        <RadarChart data={data}>
          <PolarGrid stroke="#C9BCA3" />
          <PolarAngleAxis dataKey="axis" />
          <PolarRadiusAxis angle={45} domain={[0, 100]} />
          <Radar dataKey="value" stroke="#1F3320" fill="#2D4A2B" fillOpacity={0.45} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
