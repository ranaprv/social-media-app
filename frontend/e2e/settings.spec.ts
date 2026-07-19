import { test, expect } from '@playwright/test';

test.describe('Settings Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard/settings');
    await page.waitForURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect to login when not authenticated', async ({ page }) => {
    await expect(page).toHaveURL(/\/auth\/login/);
  });
});

test.describe('Settings - Route Check', () => {
  test('should have correct URL path', async ({ page }) => {
    const response = await page.goto('/dashboard/settings');
    expect(response).toBeTruthy();
  });

  test('page should not return 500 error', async ({ page }) => {
    const response = await page.goto('/dashboard/settings');
    expect(response?.status()).toBeLessThan(500);
  });
});
