import type { Verdict } from "../../types";
import "./badges.css";

const VERDICT_META: Record<Verdict, { label: string; icon: string; className: string }> = {
  TRUE: { label: "TRUE", icon: "✓", className: "badge-good" },
  FAKE: { label: "FAKE", icon: "✕", className: "badge-critical" },
  UNVERIFIED: { label: "UNVERIFIED", icon: "?", className: "badge-warning" },
};

export function StatusBadge({ verdict }: { verdict: Verdict }) {
  const meta = VERDICT_META[verdict];
  return (
    <span className={`badge ${meta.className}`}>
      <span aria-hidden="true">{meta.icon}</span>
      {meta.label}
    </span>
  );
}
