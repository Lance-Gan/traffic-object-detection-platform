import { cameraSessionSchema, type CameraSession } from "../features/camera/camera-schema";

import { apiClient } from "./client";

export async function createCameraSession(confidenceThreshold: number): Promise<CameraSession> {
  const response = await apiClient.post("/camera/sessions", {
    confidence_threshold: confidenceThreshold,
  });

  return cameraSessionSchema.parse(response.data);
}
