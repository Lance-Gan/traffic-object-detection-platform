import type { AxiosProgressEvent } from "axios";

import {
  detectionJobDetailSchema,
  type DetectionJobDetail,
} from "../features/detections/detection-schema";
import { apiClient } from "./client";

export interface DetectImageInput {
  file: File;
  confidenceThreshold: number;
  onUploadProgress?: (percentage: number) => void;
}

function calculateUploadPercentage(
  progressEvent: AxiosProgressEvent,
  fallbackTotal: number,
): number {
  const totalBytes = progressEvent.total ?? fallbackTotal;

  if (totalBytes <= 0) {
    return 0;
  }

  return Math.min(100, Math.round((progressEvent.loaded / totalBytes) * 100));
}

export async function detectImage(input: DetectImageInput): Promise<DetectionJobDetail> {
  const formData = new FormData();

  formData.append("file", input.file);
  formData.append("confidence_threshold", input.confidenceThreshold.toFixed(2));

  const response = await apiClient.post("/detections/images", formData, {
    onUploadProgress: (progressEvent) => {
      input.onUploadProgress?.(calculateUploadPercentage(progressEvent, input.file.size));
    },
  });

  return detectionJobDetailSchema.parse(response.data);
}
