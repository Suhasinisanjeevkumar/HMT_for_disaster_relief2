export function EmptyState({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="card" style={{ textAlign: "center", padding: "40px 20px" }}>
      <p style={{ margin: 0, fontWeight: 600 }}>{title}</p>
      {hint && <p className="muted" style={{ margin: "6px 0 0" }}>{hint}</p>}
    </div>
  );
}
