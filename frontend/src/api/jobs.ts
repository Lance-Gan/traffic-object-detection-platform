import {
  detectionJobDetailSchema,
  detectionJobListSchema,
  type DetectionJobDetail,
  type DetectionJobList,
  type DetectionJobStatus,
  type DetectionSourceType,
} from "../features/detections/detection-schema";
import { apiClient } from "./client";

export interface DetectionJobFilters {
  page: number;
  pageSize: number;

  status?: DetectionJobStatus;
  sourceType?: DetectionSourceType;

  search?: string;
  createdFrom?: string;
  createdTo?: string;
}

export async function listDetectionJobs(filters: DetectionJobFilters): Promise<DetectionJobList> {
  const params = new URLSearchParams();

  params.set("page", String(filters.page));

  params.set("page_size", String(filters.pageSize));

  if (filters.status) {
    params.set("status", filters.status);
  }

  if (filters.sourceType) {
    params.set("source_type", filters.sourceType);
  }

  if (filters.search?.trim()) {
    params.set("search", filters.search.trim());
  }

  if (filters.createdFrom) {
    params.set("created_from", filters.createdFrom);
  }

  if (filters.createdTo) {
    params.set("created_to", filters.createdTo);
  }

  const response = await apiClient.get("/jobs", {
    params,
  });

  return detectionJobListSchema.parse(response.data);
}

export async function getDetectionJob(publicId: string): Promise<DetectionJobDetail> {
  const response = await apiClient.get(`/jobs/${publicId}`);

  return detectionJobDetailSchema.parse(response.data);
}
