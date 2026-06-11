import { expect, test } from "@playwright/test";

test("demo UI generates and renders a Startup Action Brief", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Minimal Demo UI" })).toBeVisible();
  await expect(page.getByText("API online")).toBeVisible({ timeout: 30_000 });
  await expect(page.getByText(/Qdrant (offline|available)/)).toBeVisible();

  await page.getByRole("button", { name: "Load example" }).click();
  await expect(page.getByLabel("Startup input JSON")).toHaveValue(/Nexus AI Labs/);

  await page.getByRole("button", { name: "Generate Startup Action Brief" }).click();

  await expect(page.getByRole("heading", { name: "Nexus AI Labs" })).toBeVisible({
    timeout: 60_000,
  });
  await expect(page.getByText("Priority score", { exact: true })).toBeVisible();
  await expect(page.getByText("Recommended motion", { exact: true })).toBeVisible();
  await expect(page.getByText("Defensibility", { exact: true })).toBeVisible();
  await expect(
    page.getByRole("heading", { name: "Production AI gaps", exact: true }),
  ).toBeVisible();
  await expect(page.getByRole("heading", { name: "Evidence used" })).toBeVisible();
  await expect(page.getByText("Markdown output", { exact: true })).toBeVisible();
  await expect(page.getByText("# Startup Action Brief: Nexus AI Labs")).toBeVisible();

  await page.getByRole("button", { name: "Evaluate brief" }).click();
  await expect(page.locator(".eval-panel .status-chip")).toContainText(/PASS|WARN|FAIL/, {
    timeout: 30_000,
  });
});

test("demo UI shows a readable API offline error", async ({ browser }) => {
  const context = await browser.newContext();
  const page = await context.newPage();
  await page.route("**/health", (route) => route.abort());
  await page.route("**/rag/status", (route) => route.abort());

  await page.goto("/");

  await expect(page.getByText(/API offline or unreachable/).first()).toBeVisible({
    timeout: 15_000,
  });

  await context.close();
});
