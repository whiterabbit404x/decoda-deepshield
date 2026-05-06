"use client";

import { Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid } from "recharts";

interface RiskTrendChartProps {
  periodLabel: string;
}

const trendData = [
  { day: "W1", high: 14, medium: 22, low: 36 },
  { day: "W2", high: 11, medium: 26, low: 32 },
  { day: "W3", high: 17, medium: 23, low: 30 },
  { day: "W4", high: 9, medium: 20, low: 28 },
  { day: "W5", high: 12, medium: 19, low: 26 },
  { day: "W6", high: 7, medium: 16, low: 25 }
];

export function RiskTrendChart({ periodLabel }: RiskTrendChartProps) {
  return (
    <article className="card chart-panel">
      <div className="panel-head">
        <h2>Risk Trend</h2>
        <span className="muted">{periodLabel}</span>
      </div>
      <div className="chart-wrap" role="img" aria-label="Risk trend chart with high, medium, and low risk series">
        <ResponsiveContainer width="100%" height={250}>
          <LineChart data={trendData}>
            <CartesianGrid stroke="#263752" strokeDasharray="4 4" />
            <XAxis dataKey="day" stroke="#9eb6d6" tickLine={false} axisLine={false} />
            <YAxis stroke="#9eb6d6" tickLine={false} axisLine={false} />
            <Tooltip contentStyle={{ background: "#091425", border: "1px solid #355798", borderRadius: 10 }} />
            <Legend wrapperStyle={{ color: "#d8e8ff", fontSize: 12 }} />
            <Line type="monotone" dataKey="high" stroke="#ff6b7e" strokeWidth={2.5} dot={false} />
            <Line type="monotone" dataKey="medium" stroke="#f5c15f" strokeWidth={2.5} dot={false} />
            <Line type="monotone" dataKey="low" stroke="#57d5ff" strokeWidth={2.5} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </article>
  );
}
