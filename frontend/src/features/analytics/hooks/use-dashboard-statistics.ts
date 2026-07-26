import { useQuery } from "@tanstack/react-query";

import { getDashboardStatistics } from "../../../api/statistics";

export function useDashboardStatistics(days: number) {
  return useQuery({
    queryKey: ["dashboard-statistics", days],

    queryFn: () => getDashboardStatistics(days),

    staleTime: 60_000,
  });
}
