import { Link, useParams } from "react-router-dom";
import { useClaim } from "../hooks/useClaims";
import { PageHeader } from "../components/layout/Layout";
import { ClaimAnalysisView } from "../components/claims/ClaimAnalysisView";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { ErrorState } from "../components/common/ErrorState";

export function ClaimDetails() {
  const { id } = useParams<{ id: string }>();
  const claimId = id ? Number(id) : undefined;
  const { data, isLoading, isError, refetch } = useClaim(claimId);

  return (
    <div className="page">
      <PageHeader
        title="Claim details"
        subtitle={<Link to="/claims">← Back to all claims</Link>}
      />

      {isLoading && <LoadingSpinner label="Loading claim…" />}
      {isError && <ErrorState message="Could not load this claim. It may not exist." onRetry={() => refetch()} />}
      {data && (
        <>
          <div className="card" style={{ marginBottom: 16 }}>
            <p style={{ margin: 0, fontSize: 16, fontWeight: 600 }}>&ldquo;{data.text}&rdquo;</p>
            <p className="muted" style={{ fontSize: 12, marginTop: 8, marginBottom: 0 }}>
              Source: {data.source} · Submitted {new Date(data.submitted_at).toLocaleString()}
              {data.is_historical_seed && " · historical IFND dataset record, not a live submission"}
              {data.source_url && (
                <> · <a href={data.source_url} target="_blank" rel="noreferrer">original source ↗</a></>
              )}
            </p>
          </div>
          <ClaimAnalysisView result={data} />
        </>
      )}
    </div>
  );
}
