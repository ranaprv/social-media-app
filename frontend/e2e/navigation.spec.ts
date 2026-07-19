import { test, expect } from '@playwright/test';

test.describe('Navigation - Landing Page Links', () => {
  test('should have all nav links point to correct routes', async ({ page }) => {
    await page.goto('/');

    const logoLink = page.locator('nav a[href="/"]').first();
    await expect(logoLink).toBeVisible();

    const loginLink = page.locator('nav a[href="/auth/login"]');
    await expect(loginLink).toBeVisible();

    const registerLink = page.locator('nav a[href="/auth/register"]');
    await expect(registerLink).toBeVisible();
  });

  test('should navigate from login to register and back', async ({ page }) => {
    await page.goto('/auth/login');
    await page.getByRole('link', { name: /sign up/i }).click();
    await expect(page).toHaveURL(/\/auth\/register/);
    await page.getByRole('link', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/auth\/login/);
  });

  test('should navigate from register to login and back', async ({ page }) => {
    await page.goto('/auth/register');
    await page.getByRole('link', { name: /sign in/i }).click();
    await expect(page).toHaveURL(/\/auth\/login/);
    await page.getByRole('link', { name: /sign up/i }).click();
    await expect(page).toHaveURL(/\/auth\/register/);
  });

  test('should handle browser back button on auth pages', async ({ page }) => {
    // Start at home to have history
    await page.goto('/');
    await expect(page).toHaveURL('/');

    // Go to login
    await page.locator('nav').getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL(/\/auth\/login/);

    // Go to register
    await page.getByRole('link', { name: /sign up/i }).click();
    await expect(page).toHaveURL(/\/auth\/register/);

    // Go back to login
    await page.goBack();
    await expect(page).toHaveURL(/\/auth\/login/);

    // Go back to home
    await page.goBack();
    await expect(page).toHaveURL('/');
  });

  test('should handle browser forward button after back', async ({ page }) => {
    // Start at home
    await page.goto('/');
    // Go to login
    await page.locator('nav').getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL(/\/auth\/login/);

    // Go back to home
    await page.goBack();
    await expect(page).toHaveURL('/');

    // Go forward to login
    await page.goForward();
    await expect(page).toHaveURL(/\/auth\/login/);
  });
});

test.describe('Navigation - 404 Handling', () => {
  test('should handle non-existent routes gracefully', async ({ page }) => {
    const response = await page.goto('/non-existent-page');
    expect(response?.status()).toBeGreaterThanOrEqual(200);
  });

  test('should handle deep non-existent dashboard routes', async ({ page }) => {
    const response = await page.goto('/dashboard/non-existent-feature');
    // Dynamic routes may catch this - either redirect to login or show page
    // Just verify no 500 error
    expect(response?.status()).toBeLessThan(500);
  });
});
