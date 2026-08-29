import { useState } from "react";
import { PageHeader } from "../components/layout/Layout";
import { useAnalyzeClaim } from "../hooks/useClaims";
import { ErrorState } from "../components/common/ErrorState";
import { LoadingSpinner } from "../components/common/LoadingSpinner";
import { ClaimAnalysisView } from "../components/claims/ClaimAnalysisView";
import { ApiError } from "../api/client";

const EXAMPLES = [
  "Heavy rainfall has caused severe flooding in Whitefield, Bengaluru.",
  "Old video of 2019 Kerala floods being shared as visuals from the current Assam flooding",
  "NDRF teams conduct rescue operation after cyclone Fani hits Odisha coast",
];

export function AnalyzeClaim() {
  const [text, setText] = useState("");
  const { mutate, data, isPending, error, reset } = useAnalyzeClaim();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    mutate(text);
  };

  return (
    <div className="page">
      <PageHeader
        title="Analyze a claim"
        subtitle="Enter a disaster-related claim to run it through the full pipeline: relevance → disaster type → location → misinformation classification → evidence → reliability → priority."
      />

      <form onSubmit={handleSubmit} className="card" style={{ marginBottom: 20 }}>
        <textarea
          rows={4}
          placeholder="e.g. Heavy rainfall has caused severe flooding in Whitefield, Bengaluru."
          value={text}
          onChange={(e) => setText(e.target.value)}
          maxLength={2000}
        />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 12, flexWrap: "wrap", gap: 8 }}>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {EXAMPLES.map((ex) => (
              <button
                type="button"
                key={ex}
                className="btn"
                style={{ fontSize: 12, padding: "5px 10px" }}
                onClick={() => setText(ex)}
              >
                {ex.slice(0, 36)}…
              </button>
            ))}
          </div>
          <button type="submit" className="btn btn-primary" disabled={isPending || !text.trim()}>
            {isPending ? "Analyzing…" : "Analyze"}
          </button>
        </div>
      </form>

      {isPending && <LoadingSpinner label="Running disaster detection → location → misinformation model → evidence lookup…" />}
      {error && (
        <ErrorState
          message={error instanceof ApiError ? error.message : "Analysis failed."}
          onRetry={() => reset()}
        />
      )}
      {data && <ClaimAnalysisView result={data} />}
    </div>
  );
}
