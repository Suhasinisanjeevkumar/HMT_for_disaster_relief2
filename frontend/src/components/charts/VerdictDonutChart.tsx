import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { usePrefersDark } from "../../hooks/useColorScheme";
import { chartTokens } from "./chartTokens";

export function VerdictDonutChart({
  trueCount,
  fakeCount,
  unverifiedCount,
}: {
  trueCount: number;
  fakeCount: number;
  unverifiedCount: number;
}) {
  const t = chartTokens(usePrefersDark());
  const data = [
    { name: "TRUE", value: trueCount, color: t.good },
    { name: "FAKE", value: fakeCount, color: t.critical },
    { name: "UNVERIFIED", value: unverifiedCount, color: t.warning },
  ];
  const total = trueCount + fakeCount + unverifiedCount;

  if (total === 0) {
    return <p className="muted">No claims analyzed yet.</p>;
  }

  return (
    <ResponsiveContainer width="100%" height={240}>
      <PieChart>
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          innerRadius={60}
          outerRadius={90}
          paddingAngle={2}
          strokeWidth={2}
          stroke="var(--surface-card)"
        >
          {data.map((d) => (
            <Cell key={d.name} fill={d.color} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value, name) => {
            const v = typeof value === "number" ? value : 0;
            return [`${v} (${((v / total) * 100).toFixed(0)}%)`, String(name)];
          }}
          contentStyle={{ background: t.tooltipBg, border: `1px solid ${t.tooltipBorder}`, borderRadius: 8 }}
          labelStyle={{ color: t.tooltipText }}
        />
        <Legend verticalAlign="bottom" height={28} iconType="circle" wrapperStyle={{ fontSize: 13 }} />
      </PieChart>
    </ResponsiveContainer>
  );
}
