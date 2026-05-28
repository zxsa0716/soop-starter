'use client';

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Line } from 'recharts';

interface FanPoint {
  year: number;
  p10_won: number;
  p50_won: number;
  p90_won: number;
  cumulative_p10_won: number;
  cumulative_p50_won: number;
  cumulative_p90_won: number;
}

export default function FanChart({
  points,
  medianCompare,
}: { points: FanPoint[]; medianCompare?: number | null }) {
  const data = points.map((p) => ({
    year: `Y${p.year}`,
    P10: p.cumulative_p10_won / 1_000_000,
    P50: p.cumulative_p50_won / 1_000_000,
    P90: p.cumulative_p90_won / 1_000_000,
    p10_p90: [p.cumulative_p10_won / 1_000_000, p.cumulative_p90_won / 1_000_000],
    median_compare: medianCompare ? medianCompare / 1_000_000 : null,
  }));

  return (
    <div className="w-full h-72 p-4 border border-stone-300 bg-white/70 rounded">
      <p className="text-xs font-mono text-bark mb-2">
        5년 누적 소득 fan chart (단위: 백만원)
      </p>
      <ResponsiveContainer width="100%" height="85%">
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#C9BCA3" />
          <XAxis dataKey="year" />
          <YAxis />
          <Tooltip />
          <Area type="monotone" dataKey="p10_p90" stroke="none" fill="#6B7E5A" fillOpacity={0.25} />
          <Line type="monotone" dataKey="P50" stroke="#1F3320" strokeWidth={2.5} dot />
          {medianCompare && (
            <Line type="monotone" dataKey="median_compare" stroke="#8B2E2E"
                  strokeWidth={1} strokeDasharray="6 3" dot={false} />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
