import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export function useMapClaims(filters: { disaster_type?: string; priority?: string }) {
  return useQuery({
    queryKey: ["map", filters],
    queryFn: () => api.mapClaims(filters),
  });
}
