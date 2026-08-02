import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.route("**/api/v1/capabilities", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        max_image_upload_bytes: 26214400,

        allowed_image_content_types: ["image/jpeg", "image/png", "image/webp"],

        default_confidence_threshold: 0.25,
      }),
    });
  });
});

test("image detection page renders", async ({ page }) => {
  await page.goto("/detect");

  await expect(page.locator("h1")).toBeVisible();

  await expect(
    page.getByRole("link", {
      name: "Image Detection",
    }),
  ).toBeVisible();
});

test("live camera page renders", async ({ page }) => {
  await page.goto("/camera");

  await expect(
    page.getByRole("heading", {
      name: "Live camera detection",
    }),
  ).toBeVisible();

  await expect(
    page.getByRole("button", {
      name: "Start live detection",
    }),
  ).toBeVisible();
});
