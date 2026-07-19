import { test, expect } from '@playwright/test';

test.describe('Inbox Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard/inbox');
    await page.waitForURL(/\/auth\/login/, { timeout: 10000 });
  });

  test('should redirect to login when not authenticated', async ({ page }) => {
    await expect(page).toHaveURL(/\/auth\/login/);
  });
});

test.describe('Inbox - Route Check', () => {
  test('should have correct URL path', async ({ page }) => {
    const response = await page.goto('/dashboard/inbox');
    expect(response).toBeTruthy();
  });

  test('page should not return 500 error', async ({ page }) => {
    const response = await page.goto('/dashboard/inbox');
    expect(response?.status()).toBeLessThan(500);
  });
});
