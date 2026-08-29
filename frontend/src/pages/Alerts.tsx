import { useState } from "react";
import { PageHeader } from "../components/layout/Layout";
import { useAlerts, useAcknowledgeAlert } from "../hooks/useAlerts";
import { AlertList } from "../components/alerts/AlertList";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { ErrorState } from "../components/common/ErrorState";

export function Alerts() {
  const [showAcknowledged, setShowAcknowledged] = useState(false);
  const { data, isLoading, isError, refetch } = useAlerts(showAcknowledged ? {} : { acknowledged: false });
  const acknowledge = useAcknowledgeAlert();

  return (
    <div className="page">
      <PageHeader
        title="Alerts"
        subtitle="High-priority, well-supported (or confidently-fake) claims flagged for relief-organization consideration. No emergency services are contacted by this system."
      />

      <label style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16, fontSize: 14 }}>
        <input type="checkbox" checked={showAcknowledged} onChange={(e) => setShowAcknowledged(e.target.checked)} />
        Show acknowledged alerts too
      </label>

      {isLoading && <LoadingSpinner label="Loading alerts…" />}
      {isError && <ErrorState message="Could not load alerts." onRetry={() => refetch()} />}
      {data && (
        <AlertList
          alerts={data.items}
          onAcknowledge={(id) => acknowledge.mutate(id)}
          acknowledgingId={acknowledge.isPending ? (acknowledge.variables ?? null) : null}
        />
      )}
    </div>
  );
}
