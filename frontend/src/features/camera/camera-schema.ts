import { z } from "zod";

export const cameraSessionSchema = z.object({
  public_id: z.string().uuid(),

  status: z.enum(["pending", "processing", "completed", "failed"]),

  websocket_path: z.string().min(1),

  target_fps: z.number().int().positive(),

  frame_width: z.number().int().positive(),

  jpeg_quality: z.number().gt(0).max(1),

  max_frame_bytes: z.number().int().positive(),

  max_session_seconds: z.number().int().positive(),
});

export const cameraObjectSchema = z.object({
  track_id: z.number().int().nullable(),

  class_id: z.number().int().nonnegative(),

  class_name: z.string().min(1),

  confidence: z.number().min(0).max(1),

  bounding_box: z.object({
    x1: z.number(),
    y1: z.number(),
    x2: z.number(),
    y2: z.number(),
  }),
});

export const cameraSessionMetricsSchema = z.object({
  processed_frames: z.number().int().nonnegative(),

  total_detections: z.number().int().nonnegative(),

  unique_objects: z.number().int().nonnegative(),

  elapsed_ms: z.number().int().nonnegative(),
});

const cameraLoadingMessageSchema = z.object({
  type: z.literal("loading_model"),
  message: z.string(),
});

const cameraReadyMessageSchema = z.object({
  type: z.literal("ready"),

  device: z.string(),
  model_name: z.string(),

  target_fps: z.number().int().positive(),

  max_session_seconds: z.number().int().positive(),
});

export const cameraFrameMessageSchema = z.object({
  type: z.literal("frame_result"),

  frame_index: z.number().int().nonnegative(),

  frame_width: z.number().int().positive(),

  frame_height: z.number().int().positive(),

  inference_ms: z.number().int().nonnegative(),

  server_fps: z.number().nonnegative(),

  objects: z.array(cameraObjectSchema),

  summary: z.record(z.string(), z.number().int().nonnegative()),

  session: cameraSessionMetricsSchema,
});

const cameraErrorMessageSchema = z.object({
  type: z.literal("error"),
  message: z.string(),
  fatal: z.boolean(),
});

const cameraPongMessageSchema = z.object({
  type: z.literal("pong"),
});

const cameraCompletedMessageSchema = z.object({
  type: z.literal("session_completed"),

  public_id: z.string().uuid(),
  stop_reason: z.string(),

  processed_frames: z.number().int().nonnegative(),

  total_detections: z.number().int().nonnegative(),

  unique_objects: z.number().int().nonnegative(),

  duration_ms: z.number().int().nonnegative(),
});

export const cameraServerMessageSchema = z.discriminatedUnion("type", [
  cameraLoadingMessageSchema,
  cameraReadyMessageSchema,
  cameraFrameMessageSchema,
  cameraErrorMessageSchema,
  cameraPongMessageSchema,
  cameraCompletedMessageSchema,
]);

export type CameraSession = z.infer<typeof cameraSessionSchema>;

export type CameraFrameMessage = z.infer<typeof cameraFrameMessageSchema>;

export type CameraServerMessage = z.infer<typeof cameraServerMessageSchema>;

export type CameraCompletedMessage = z.infer<typeof cameraCompletedMessageSchema>;
