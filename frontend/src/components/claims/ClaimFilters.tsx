import type { ClaimFilters as Filters } from "../../types";

const DISASTER_TYPES = [
  "Flood", "Cyclone", "Earthquake", "Landslide", "Heavy Rain", "Cloudburst",
  "Drought", "Wildfire", "Tsunami", "Avalanche", "Storm", "Rescue/Evacuation", "Other",
];

export function ClaimFilters({
  filters,
  onChange,
}: {
  filters: Filters;
  onChange: (f: Filters) => void;
}) {
  return (
    <div className="card" style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "flex-end" }}>
      <div style={{ flex: "1 1 220px" }}>
        <label htmlFor="q" style={{ display: "block", fontSize: 12, color: "var(--text-muted)", marginBottom: 4 }}>
          Search
        </label>
        <input
          id="q"
          className="input"
          placeholder="Search claim text or location…"
          value={filters.q ?? ""}
          onChange={(e) => onChange({ ...filters, q: e.target.value || undefined, offset: 0 })}
        />
      </div>
      <FilterSelect
        label="Verdict"
        value={filters.verdict}
        options={["TRUE", "FAKE", "UNVERIFIED"]}
        onChange={(v) => onChange({ ...filters, verdict: v, offset: 0 })}
      />
      <FilterSelect
        label="Disaster type"
        value={filters.disaster_type}
        options={DISASTER_TYPES}
        onChange={(v) => onChange({ ...filters, disaster_type: v, offset: 0 })}
      />
      <FilterSelect
        label="Priority"
        value={filters.priority}
        options={["HIGH", "MEDIUM", "LOW"]}
        onChange={(v) => onChange({ ...filters, priority: v, offset: 0 })}
      />
    </div>
  );
}

function FilterSelect({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string | undefined;
  options: string[];
  onChange: (v: string | undefined) => void;
}) {
  return (
    <div>
      <label style={{ display: "block", fontSize: 12, color: "var(--text-muted)", marginBottom: 4 }}>{label}</label>
      <select
        className="input"
        value={value ?? ""}
        onChange={(e) => onChange(e.target.value || undefined)}
        style={{ minWidth: 140 }}
      >
        <option value="">All</option>
        {options.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </div>
  );
}
