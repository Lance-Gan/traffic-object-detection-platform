import { useQuery } from "@tanstack/react-query";

import { getSystemStatus } from "../../../api/health";

export function useSystemStatus() {
  return useQuery({
    queryKey: ["system-status"],

    queryFn: getSystemStatus,

    refetchInterval: 30_000,
    staleTime: 10_000,
  });
}
