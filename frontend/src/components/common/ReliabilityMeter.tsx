import type { ReliabilityBand } from "../../types";

// Reliability: higher band = better support for the verdict, so the color
// direction is inverted relative to PriorityBadge (where HIGH = most urgent
// = critical red). Here HIGH = well-supported = good green.
const BAND_COLOR: Record<ReliabilityBand, string> = {
  HIGH: "var(--status-good)",
  MEDIUM: "var(--status-warning)",
  LOW: "var(--status-critical)",
};

export function ReliabilityMeter({ score, band }: { score: number | null; band: ReliabilityBand | null }) {
  if (score === null || band === null) {
    return <span className="muted">Not yet scored</span>;
  }
  const color = BAND_COLOR[band];
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
      <div
        style={{
          flex: 1,
          height: 8,
          borderRadius: 999,
          background: "var(--gridline)",
          overflow: "hidden",
          maxWidth: 160,
        }}
        role="meter"
        aria-valuenow={score}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Reliability score ${score} out of 100, ${band}`}
      >
        <div style={{ width: `${score}%`, height: "100%", background: color, borderRadius: 999 }} />
      </div>
      <span style={{ fontWeight: 600, fontSize: "0.85rem", color }}>
        {score}/100 &middot; {band}
      </span>
    </div>
  );
}
