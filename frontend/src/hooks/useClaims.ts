import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";
import type { ClaimFilters } from "../types";

export function useClaims(filters: ClaimFilters) {
  return useQuery({
    queryKey: ["claims", filters],
    queryFn: () => api.listClaims(filters),
  });
}

export function useClaim(id: number | undefined) {
  return useQuery({
    queryKey: ["claim", id],
    queryFn: () => api.getClaim(id as number),
    enabled: id !== undefined,
  });
}

export function useAnalyzeClaim() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (text: string) => api.analyzeClaim(text),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["claims"] });
      queryClient.invalidateQueries({ queryKey: ["stats"] });
      queryClient.invalidateQueries({ queryKey: ["map"] });
      queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });
}
