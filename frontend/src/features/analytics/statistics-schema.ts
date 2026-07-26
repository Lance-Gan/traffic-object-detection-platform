import { z } from "zod";

import { detectionSourceTypeSchema } from "../detections/detection-schema";

export const dashboardStatisticsSchema = z.object({
  period: z.object({
    days: z.number().int().positive(),
    start_date: z.string(),
    end_date: z.string(),
    timezone: z.string(),
  }),

  metrics: z.object({
    total_jobs: z.number().int().nonnegative(),

    completed_jobs: z.number().int().nonnegative(),

    failed_jobs: z.number().int().nonnegative(),

    processing_jobs: z.number().int().nonnegative(),

    pending_jobs: z.number().int().nonnegative(),

    total_detected_objects: z.number().int().nonnegative(),

    success_rate: z.number().min(0).max(100),

    average_confidence: z.number().min(0).max(1).nullable(),

    average_duration_ms: z.number().nonnegative().nullable(),
  }),

  classes: z.array(
    z.object({
      class_name: z.string(),
      object_count: z.number().int().nonnegative(),

      average_confidence: z.number().min(0).max(1).nullable(),
    }),
  ),

  daily: z.array(
    z.object({
      date: z.string(),

      total_jobs: z.number().int().nonnegative(),

      completed_jobs: z.number().int().nonnegative(),

      failed_jobs: z.number().int().nonnegative(),

      detected_objects: z.number().int().nonnegative(),
    }),
  ),

  sources: z.array(
    z.object({
      source_type: detectionSourceTypeSchema,

      job_count: z.number().int().nonnegative(),
    }),
  ),
});

export type DashboardStatistics = z.infer<typeof dashboardStatisticsSchema>;
