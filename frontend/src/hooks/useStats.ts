import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export function useStatsOverview() {
  return useQuery({ queryKey: ["stats", "overview"], queryFn: api.statsOverview });
}

export function useDisasterTypeStats() {
  return useQuery({ queryKey: ["stats", "disaster-types"], queryFn: api.statsDisasterTypes });
}

export function useTopLocations(by: "state" | "city" = "state", limit = 10) {
  return useQuery({
    queryKey: ["stats", "locations", by, limit],
    queryFn: () => api.statsLocations(by, limit),
  });
}

export function useTimeline() {
  return useQuery({ queryKey: ["stats", "timeline"], queryFn: api.statsTimeline });
}
