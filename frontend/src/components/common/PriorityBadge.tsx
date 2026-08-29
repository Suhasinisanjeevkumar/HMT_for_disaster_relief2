import type { PriorityLevel } from "../../types";
import "./badges.css";

const PRIORITY_META: Record<PriorityLevel, { icon: string; className: string }> = {
  HIGH: { icon: "▲", className: "badge-critical" },
  MEDIUM: { icon: "●", className: "badge-warning" },
  LOW: { icon: "▽", className: "badge-good" },
};

export function PriorityBadge({ level }: { level: PriorityLevel }) {
  const meta = PRIORITY_META[level];
  return (
    <span className={`badge ${meta.className}`}>
      <span aria-hidden="true">{meta.icon}</span>
      {level}
    </span>
  );
}
