import { test, expect } from '@playwright/test';

test.describe('Dashboard Auth Guard', () => {
  test('should redirect to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard');
    // AuthGuard should redirect unauthenticated users to login
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect content-studio to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/content-studio');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect analytics to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/analytics');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect calendar to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/calendar');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect inbox to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/inbox');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect team to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/team');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect billing to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/billing');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect settings to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/settings');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect research to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/research');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect repurpose to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/repurpose');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect media to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/media');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect listening to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/listening');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect ai-assistant to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/ai-assistant');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect recommendations to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/recommendations');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect ads to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/ads');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect reports to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/reports');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect competitors to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/competitors');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect connections to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/connections');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect approvals to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/approvals');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect tasks to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/tasks');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect automation to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/automation');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect advocacy to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/advocacy');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect security to login when not authenticated', async ({ page }) => {
    await page.goto('/dashboard/security');
    await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
  });
});
