export function LoadingSpinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 10, padding: "32px 0", color: "var(--text-muted)" }}>
      <span
        aria-hidden="true"
        style={{
          width: 16,
          height: 16,
          border: "2px solid var(--gridline)",
          borderTopColor: "var(--series-1)",
          borderRadius: "50%",
          display: "inline-block",
          animation: "hmt-spin 0.7s linear infinite",
        }}
      />
      <span>{label}</span>
      <style>{`@keyframes hmt-spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
