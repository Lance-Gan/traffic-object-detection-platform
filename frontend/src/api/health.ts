import {
  databaseHealthSchema,
  systemHealthSchema,
  type DatabaseHealth,
  type SystemHealth,
} from "../features/system/system-schema";

import { apiClient } from "./client";

export interface SystemStatus {
  system: SystemHealth;
  database: DatabaseHealth;
}

export async function getSystemStatus(): Promise<SystemStatus> {
  const [systemResponse, databaseResponse] = await Promise.all([
    apiClient.get("/health/system"),
    apiClient.get("/health/database"),
  ]);

  return {
    system: systemHealthSchema.parse(systemResponse.data),

    database: databaseHealthSchema.parse(databaseResponse.data),
  };
}
