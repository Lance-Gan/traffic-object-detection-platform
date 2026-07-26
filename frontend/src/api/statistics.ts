import {
  dashboardStatisticsSchema,
  type DashboardStatistics,
} from "../features/analytics/statistics-schema";
import { apiClient } from "./client";

export async function getDashboardStatistics(days: number): Promise<DashboardStatistics> {
  const response = await apiClient.get("/statistics/dashboard", {
    params: {
      days,
    },
  });

  return dashboardStatisticsSchema.parse(response.data);
}
