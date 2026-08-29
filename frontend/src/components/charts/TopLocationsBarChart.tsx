import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { usePrefersDark } from "../../hooks/useColorScheme";
import { chartTokens } from "./chartTokens";
import type { CountItem } from "../../types";

export function TopLocationsBarChart({ data }: { data: CountItem[] }) {
  const t = chartTokens(usePrefersDark());

  if (data.length === 0) {
    return <p className="muted">No locations resolved yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={Math.max(220, data.length * 32)}>
      <BarChart data={data} layout="vertical" margin={{ top: 4, right: 16, left: 8, bottom: 4 }}>
        <CartesianGrid horizontal={false} stroke={t.grid} />
        <XAxis type="number" tick={{ fill: t.axis, fontSize: 11 }} allowDecimals={false} />
        <YAxis type="category" dataKey="label" tick={{ fill: t.axis, fontSize: 12 }} width={110} />
        <Tooltip
          cursor={{ fill: "transparent" }}
          contentStyle={{ background: t.tooltipBg, border: `1px solid ${t.tooltipBorder}`, borderRadius: 8 }}
          labelStyle={{ color: t.tooltipText }}
        />
        <Bar dataKey="count" fill={t.seriesBlue} radius={[0, 4, 4, 0]} maxBarSize={18} />
      </BarChart>
    </ResponsiveContainer>
  );
}
