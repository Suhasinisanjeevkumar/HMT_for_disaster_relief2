import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { usePrefersDark } from "../../hooks/useColorScheme";
import { chartTokens } from "./chartTokens";
import type { TimelinePoint } from "../../types";

export function ClaimsTimelineChart({ data }: { data: TimelinePoint[] }) {
  const t = chartTokens(usePrefersDark());

  if (data.length === 0) {
    return <p className="muted">No claims analyzed yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={240}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
        <CartesianGrid vertical={false} stroke={t.grid} />
        <XAxis dataKey="date" tick={{ fill: t.axis, fontSize: 11 }} minTickGap={24} />
        <YAxis tick={{ fill: t.axis, fontSize: 11 }} allowDecimals={false} />
        <Tooltip
          contentStyle={{ background: t.tooltipBg, border: `1px solid ${t.tooltipBorder}`, borderRadius: 8 }}
          labelStyle={{ color: t.tooltipText }}
        />
        <Line
          type="monotone"
          dataKey="count"
          stroke={t.seriesBlue}
          strokeWidth={2}
          dot={{ r: 3, fill: t.seriesBlue, stroke: "var(--surface-card)", strokeWidth: 2 }}
          activeDot={{ r: 5 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
