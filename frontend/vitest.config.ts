import react from "@vitejs/plugin-react";
import { configDefaults, defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],

  test: {
    environment: "jsdom",

    setupFiles: ["./src/test/setup.ts"],

    clearMocks: true,
    restoreMocks: true,

    exclude: [
      ...configDefaults.exclude,
      "e2e/**",
      "coverage/**",
      "playwright-report/**",
      "test-results/**",
    ],

    coverage: {
      provider: "v8",

      reporter: ["text", "html", "lcov"],

      reportsDirectory: "./coverage",

      include: ["src/**/*.{ts,tsx}"],

      exclude: ["src/main.tsx", "src/**/*.d.ts", "src/test/**"],
    },
  },
});
