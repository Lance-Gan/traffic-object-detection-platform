import { z } from "zod";

const envSchema = z.object({
  VITE_API_BASE_URL: z.string().min(1).default("/api/v1"),

  VITE_MAX_IMAGE_UPLOAD_BYTES: z.coerce
    .number()
    .int()
    .positive()
    .default(25 * 1024 * 1024),
});

const parsedEnvironment = envSchema.safeParse(import.meta.env);

if (!parsedEnvironment.success) {
  console.error(
    "Invalid frontend environment configuration",
    parsedEnvironment.error.flatten().fieldErrors,
  );

  throw new Error("Invalid frontend environment configuration");
}

export const env = parsedEnvironment.data;
