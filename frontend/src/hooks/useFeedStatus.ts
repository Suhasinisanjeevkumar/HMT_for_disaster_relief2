import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";

export function useFeedStatus() {
  return useQuery({
    queryKey: ["feed-status"],
    queryFn: api.feedStatus,
    refetchInterval: 60_000, // poll -- this is a periodic-monitoring status display, not a live stream
  });
}
