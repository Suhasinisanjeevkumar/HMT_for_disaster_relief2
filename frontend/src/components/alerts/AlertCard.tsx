import { Link } from "react-router-dom";
import type { AlertOut } from "../../types";
import { PriorityBadge } from "../common/PriorityBadge";
import "../common/badges.css";

export function AlertCard({
  alert,
  onAcknowledge,
  acknowledging,
}: {
  alert: AlertOut;
  onAcknowledge: (id: number) => void;
  acknowledging: boolean;
}) {
  return (
    <div className="card" style={{ opacity: alert.acknowledged ? 0.6 : 1 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
        <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
          <span aria-hidden="true">🚨</span>
          <PriorityBadge level={alert.level} />
          <span className="muted" style={{ fontSize: 12 }}>
            {new Date(alert.created_at).toLocaleString()}
          </span>
        </div>
        {!alert.acknowledged && (
          <button className="btn" onClick={() => onAcknowledge(alert.id)} disabled={acknowledging}>
            {acknowledging ? "…" : "Acknowledge"}
          </button>
        )}
        {alert.acknowledged && <span className="badge badge-good">Acknowledged</span>}
      </div>
      <p style={{ margin: "10px 0" }}>{alert.reason_text}</p>
      <Link to={`/claims/${alert.claim_id}`} style={{ fontSize: 13 }}>
        View full claim details →
      </Link>
    </div>
  );
}
