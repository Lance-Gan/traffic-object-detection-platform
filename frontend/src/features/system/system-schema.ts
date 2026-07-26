import { z } from "zod";

export const systemHealthSchema = z.object({
  status: z.literal("ok"),
  service: z.string(),

  version: z.string(),
  environment: z.string(),

  python_version: z.string(),

  model_name: z.string(),
  configured_device: z.string(),
  mps_available: z.boolean(),

  max_image_upload_bytes: z.number().int().positive(),
});

export const databaseHealthSchema = z.object({
  status: z.literal("ok"),
  service: z.string(),
  database: z.string(),
});

export type SystemHealth = z.infer<typeof systemHealthSchema>;

export type DatabaseHealth = z.infer<typeof databaseHealthSchema>;
