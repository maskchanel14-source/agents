import path from "node:path";
import { expect, test } from "@playwright/test";

/**
 * End-to-end: register → upload → analyze → clip library → caption editor.
 * Requires the API (8000) and web app (3000) running, plus `make sample`.
 */
const SAMPLE = process.env.E2E_SAMPLE || path.resolve(__dirname, "../../../data/sample.mp4");
const email = `e2e-${Date.now()}@example.com`;
const password = "e2e-password-123";

test.describe.configure({ mode: "serial" });

test("registration lands on the dashboard", async ({ page }) => {
  await page.goto("/login");
  await page.getByRole("button", { name: "Create account" }).first().click();
  await page.getByLabel("Name").fill("E2E Tester");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.locator('button[type="submit"]').click();
  await expect(page).toHaveURL(/\/dashboard/, { timeout: 30_000 });
  await expect(page.getByRole("heading", { level: 1 })).toContainText("Welcome back");
});

test("full clip generation flow", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill(email);
  await page.getByLabel("Password").fill(password);
  await page.locator('button[type="submit"]').click();
  await expect(page).toHaveURL(/\/dashboard/, { timeout: 30_000 });

  await page.getByRole("link", { name: "New project" }).first().click();
  await expect(page.getByRole("heading", { name: /Analyze a video/i })).toBeVisible();

  await page.setInputFiles('input[type="file"]', SAMPLE);
  await page.getByLabel("Project title").fill("E2E podcast");
  await page.getByRole("button", { name: /Analyze video/i }).click();

  await expect(page).toHaveURL(/\/projects\/.+\/analysis/, { timeout: 90_000 });
  await expect(page.getByRole("link", { name: "View clips" })).toBeVisible();
  await page.getByRole("link", { name: "View clips" }).click();

  await expect(page).toHaveURL(/\/clips$/);
  await expect(page.getByText(/potential/i).first()).toBeVisible({ timeout: 180_000 });

  await page.getByRole("link", { name: "Captions" }).first().click();
  await expect(page).toHaveURL(/\/subtitles$/);

  await page.goto("/export");
  await expect(page.getByRole("heading", { name: /Deliver to Shorts/i })).toBeVisible();
});

test("unauthenticated visitors are redirected to login", async ({ page }) => {
  await page.context().clearCookies();
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/login/);
});
