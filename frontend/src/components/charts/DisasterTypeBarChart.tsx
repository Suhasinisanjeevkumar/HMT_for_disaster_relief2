import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { usePrefersDark } from "../../hooks/useColorScheme";
import { chartTokens } from "./chartTokens";
import type { CountItem } from "../../types";

export function DisasterTypeBarChart({ data }: { data: CountItem[] }) {
  const t = chartTokens(usePrefersDark());

  if (data.length === 0) {
    return <p className="muted">No claims analyzed yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 8 }}>
        <CartesianGrid vertical={false} stroke={t.grid} />
        <XAxis
          dataKey="label"
          tick={{ fill: t.axis, fontSize: 11 }}
          angle={-30}
          textAnchor="end"
          interval={0}
          height={60}
        />
        <YAxis tick={{ fill: t.axis, fontSize: 11 }} allowDecimals={false} />
        <Tooltip
          cursor={{ fill: "transparent" }}
          contentStyle={{ background: t.tooltipBg, border: `1px solid ${t.tooltipBorder}`, borderRadius: 8 }}
          labelStyle={{ color: t.tooltipText }}
        />
        <Bar dataKey="count" fill={t.seriesBlue} radius={[4, 4, 0, 0]} maxBarSize={24} />
      </BarChart>
    </ResponsiveContainer>
  );
}
