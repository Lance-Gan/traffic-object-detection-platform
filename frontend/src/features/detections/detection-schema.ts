import { z } from "zod";

export const detectionJobStatusSchema = z.enum(["pending", "processing", "completed", "failed"]);

export const detectionSourceTypeSchema = z.enum(["image", "video", "camera"]);

export const boundingBoxSchema = z.object({
  x1: z.number(),
  y1: z.number(),
  x2: z.number(),
  y2: z.number(),
});

export const detectionObjectSchema = z.object({
  frame_index: z.number().int().nonnegative(),

  track_id: z.number().int().nullable(),

  class_id: z.number().int().nonnegative(),

  class_name: z.string().min(1),

  confidence: z.number().min(0).max(1),

  bounding_box: boundingBoxSchema,
});

export const detectionJobSummarySchema = z.object({
  public_id: z.string().uuid(),

  source_type: detectionSourceTypeSchema,

  status: detectionJobStatusSchema,

  original_filename: z.string().min(1),

  result_url: z.string().nullable(),

  detected_object_count: z.number().int().nonnegative(),

  duration_ms: z.number().int().nonnegative().nullable(),

  progress_percent: z.number().int().min(0).max(100),

  unique_object_count: z.number().int().nonnegative(),

  total_frames: z.number().int().nonnegative().nullable(),

  processed_frames: z.number().int().nonnegative().nullable(),

  summary: z.record(z.string(), z.number().int().nonnegative()),

  created_at: z.string().min(1),

  completed_at: z.string().nullable(),
});

export const detectionJobDetailSchema = detectionJobSummarySchema.extend({
  model_name: z.string().min(1),

  device: z.string().min(1),

  confidence_threshold: z.number().min(0).max(1),

  file_size_bytes: z.number().int().nonnegative(),

  video_duration_ms: z.number().int().nonnegative().nullable(),

  objects: z.array(detectionObjectSchema),
});

export const detectionJobListSchema = z.object({
  items: z.array(detectionJobSummarySchema),

  page: z.number().int().positive(),

  page_size: z.number().int().positive(),

  count: z.number().int().nonnegative(),

  total: z.number().int().nonnegative(),

  total_pages: z.number().int().nonnegative(),

  has_previous: z.boolean(),

  has_next: z.boolean(),
});

export type DetectionJobStatus = z.infer<typeof detectionJobStatusSchema>;

export type DetectionSourceType = z.infer<typeof detectionSourceTypeSchema>;

export type DetectionJobSummary = z.infer<typeof detectionJobSummarySchema>;

export type DetectionJobDetail = z.infer<typeof detectionJobDetailSchema>;

export type DetectionJobList = z.infer<typeof detectionJobListSchema>;
