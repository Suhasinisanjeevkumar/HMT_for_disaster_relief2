import { useState } from "react";
import { PageHeader } from "../components/layout/Layout";
import { useClaims } from "../hooks/useClaims";
import { ClaimFilters } from "../components/claims/ClaimFilters";
import { ClaimTable } from "../components/claims/ClaimTable";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { ErrorState } from "../components/common/ErrorState";
import type { ClaimFilters as Filters } from "../types";

const PAGE_SIZE = 20;

export function Claims() {
  const [filters, setFilters] = useState<Filters>({ limit: PAGE_SIZE, offset: 0 });
  const { data, isLoading, isError, refetch } = useClaims(filters);

  const offset = filters.offset ?? 0;
  const page = Math.floor(offset / PAGE_SIZE) + 1;
  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  return (
    <div className="page">
      <PageHeader title="Claims" subtitle="All analyzed claims — live-submitted and the seeded historical dataset. Search and filter to find specific reports." />

      <div style={{ marginBottom: 16 }}>
        <ClaimFilters filters={filters} onChange={setFilters} />
      </div>

      {isLoading && <LoadingSpinner label="Loading claims…" />}
      {isError && <ErrorState message="Could not load claims." onRetry={() => refetch()} />}
      {data && (
        <>
          <div className="card">
            <ClaimTable claims={data.items} />
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 14 }}>
            <span className="muted" style={{ fontSize: 13 }}>
              {data.total} total claim{data.total === 1 ? "" : "s"} · page {page} of {totalPages}
            </span>
            <div style={{ display: "flex", gap: 8 }}>
              <button
                className="btn"
                disabled={offset === 0}
                onClick={() => setFilters((f) => ({ ...f, offset: Math.max(0, offset - PAGE_SIZE) }))}
              >
                ← Previous
              </button>
              <button
                className="btn"
                disabled={offset + PAGE_SIZE >= data.total}
                onClick={() => setFilters((f) => ({ ...f, offset: offset + PAGE_SIZE }))}
              >
                Next →
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
