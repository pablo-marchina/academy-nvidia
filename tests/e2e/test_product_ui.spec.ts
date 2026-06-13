import { expect, test } from "@playwright/test";

test("Product UI readiness page loads and shows status", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByText("NVIDIA Startup AI Radar")).toBeVisible();
  await expect(page.getByText("Product UI")).toBeVisible();

  await expect(page.getByRole("button", { name: "Setup" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Capabilities" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Startups" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Opportunities" })).toBeVisible();

  await expect(page.getByText(/Ready|Not Ready/).first()).toBeVisible({ timeout: 30_000 });
});

test("Product UI capabilities page loads and shows capabilities", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Capabilities" }).click();
  await expect(page.getByText("Product Capabilities")).toBeVisible();

  await expect(page.getByText("core").first()).toBeVisible({ timeout: 15_000 });
});
