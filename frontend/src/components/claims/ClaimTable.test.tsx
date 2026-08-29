import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { ClaimTable } from "./ClaimTable";
import type { ClaimOut } from "../../types";

const SAMPLE: ClaimOut = {
  id: 1,
  text: "Heavy rainfall has caused severe flooding in Whitefield, Bengaluru.",
  source: "manual",
  source_url: null,
  submitted_at: "2026-08-29T10:00:00Z",
  disaster_type: "Flood",
  classification: "TRUE",
  confidence: 0.78,
  reliability_score: 54,
  reliability_band: "MEDIUM",
  priority: "MEDIUM",
  priority_score: 4,
  verification_status: "not_matched",
  is_historical_seed: false,
};

function renderWithRouter(children: React.ReactNode) {
  return render(<MemoryRouter>{children}</MemoryRouter>);
}

describe("ClaimTable", () => {
  it("shows an empty state when there are no claims", () => {
    renderWithRouter(<ClaimTable claims={[]} />);
    expect(screen.getByText(/no claims match these filters/i)).toBeInTheDocument();
  });

  it("renders a row per claim with verdict, priority, and disaster type", () => {
    renderWithRouter(<ClaimTable claims={[SAMPLE]} />);
    expect(screen.getByText(/heavy rainfall/i)).toBeInTheDocument();
    expect(screen.getByText("Flood")).toBeInTheDocument();
    expect(screen.getByText("TRUE")).toBeInTheDocument();
    expect(screen.getByText("MEDIUM")).toBeInTheDocument();
  });

  it("marks historical-seed claims distinctly from live submissions", () => {
    renderWithRouter(<ClaimTable claims={[{ ...SAMPLE, is_historical_seed: true }]} />);
    expect(screen.getByText(/historical/i)).toBeInTheDocument();
  });
});
