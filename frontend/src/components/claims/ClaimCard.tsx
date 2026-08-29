import { Link } from "react-router-dom";
import type { ClaimOut } from "../../types";
import { StatusBadge } from "../common/StatusBadge";
import { PriorityBadge } from "../common/PriorityBadge";

export function ClaimCard({ claim }: { claim: ClaimOut }) {
  return (
    <Link to={`/claims/${claim.id}`} className="card" style={{ display: "block", textDecoration: "none", color: "inherit" }}>
      <div style={{ display: "flex", gap: 8, marginBottom: 8, flexWrap: "wrap" }}>
        <StatusBadge verdict={claim.classification} />
        <PriorityBadge level={claim.priority} />
        <span className="muted" style={{ fontSize: 12, marginLeft: "auto" }}>
          {new Date(claim.submitted_at).toLocaleDateString()}
        </span>
      </div>
      <p style={{ margin: 0, fontSize: 14, lineHeight: 1.4 }}>
        {claim.text.length > 140 ? `${claim.text.slice(0, 140)}…` : claim.text}
      </p>
      <p className="muted" style={{ margin: "8px 0 0", fontSize: 12 }}>
        {claim.disaster_type}
        {claim.reliability_score !== null && ` · reliability ${claim.reliability_score}/100`}
      </p>
    </Link>
  );
}
