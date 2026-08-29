import type { AlertOut } from "../../types";
import { AlertCard } from "./AlertCard";
import { EmptyState } from "../common/EmptyState";

export function AlertList({
  alerts,
  onAcknowledge,
  acknowledgingId,
}: {
  alerts: AlertOut[];
  onAcknowledge: (id: number) => void;
  acknowledgingId: number | null;
}) {
  if (alerts.length === 0) {
    return (
      <EmptyState
        title="No alerts"
        hint="Alerts appear here for HIGH-priority claims that are well-supported or confidently classified as misinformation."
      />
    );
  }
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {alerts.map((a) => (
        <AlertCard key={a.id} alert={a} onAcknowledge={onAcknowledge} acknowledging={acknowledgingId === a.id} />
      ))}
    </div>
  );
}
