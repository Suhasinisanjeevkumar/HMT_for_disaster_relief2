export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div
      className="card"
      style={{ borderColor: "color-mix(in srgb, var(--status-critical) 40%, var(--border))" }}
      role="alert"
    >
      <div style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
        <span aria-hidden="true" style={{ color: "var(--status-critical)", fontSize: "1.1rem" }}>⚠</span>
        <div>
          <p style={{ margin: 0, fontWeight: 600 }}>Something went wrong</p>
          <p className="muted" style={{ margin: "4px 0 0" }}>{message}</p>
          {onRetry && (
            <button className="btn" style={{ marginTop: 10 }} onClick={onRetry}>
              Try again
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
