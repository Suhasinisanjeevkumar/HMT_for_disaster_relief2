import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../api/client";

export function useAlerts(filters: { acknowledged?: boolean; level?: string } = {}) {
  return useQuery({
    queryKey: ["alerts", filters],
    queryFn: () => api.listAlerts(filters),
  });
}

export function useAcknowledgeAlert() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.acknowledgeAlert(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["alerts"] }),
  });
}
