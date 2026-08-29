import { Link } from "react-router-dom";
import type { ClaimOut } from "../../types";
import { StatusBadge } from "../common/StatusBadge";
import { PriorityBadge } from "../common/PriorityBadge";
import { EmptyState } from "../common/EmptyState";

export function ClaimTable({ claims }: { claims: ClaimOut[] }) {
  if (claims.length === 0) {
    return <EmptyState title="No claims match these filters" hint="Try broadening your search or filters." />;
  }

  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            <th>Claim</th>
            <th>Disaster</th>
            <th>Verdict</th>
            <th>Priority</th>
            <th>Reliability</th>
            <th>Submitted</th>
          </tr>
        </thead>
        <tbody>
          {claims.map((c) => (
            <tr key={c.id}>
              <td style={{ whiteSpace: "normal", maxWidth: 360 }}>
                <Link to={`/claims/${c.id}`}>{c.text.length > 100 ? `${c.text.slice(0, 100)}…` : c.text}</Link>
                {c.is_historical_seed && <span className="muted" style={{ fontSize: 11, marginLeft: 6 }}>historical</span>}
              </td>
              <td>{c.disaster_type}</td>
              <td><StatusBadge verdict={c.classification} /></td>
              <td><PriorityBadge level={c.priority} /></td>
              <td>{c.reliability_score !== null ? `${c.reliability_score}/100` : "—"}</td>
              <td>{new Date(c.submitted_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
