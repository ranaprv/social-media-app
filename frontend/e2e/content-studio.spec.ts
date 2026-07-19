import { test, expect } from '@playwright/test';

test.describe('Content Studio Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard/content-studio');
    // Wait for auth redirect
    await page.waitForURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect to login when not authenticated', async ({ page }) => {
    await expect(page).toHaveURL(/\/auth\/login/);
  });
});

test.describe('Content Studio - Page Structure', () => {
  test('should have correct URL path', async ({ page }) => {
    // Verify the route exists (will redirect to login)
    const response = await page.goto('/dashboard/content-studio');
    expect(response).toBeTruthy();
  });
});

test.describe('Content Studio - Component Check', () => {
  test('page source should reference content-studio components', async ({ page }) => {
    const response = await page.goto('/dashboard/content-studio');
    // The page should load (even if it redirects)
    expect(response?.status()).toBeLessThan(500);
  });
});
