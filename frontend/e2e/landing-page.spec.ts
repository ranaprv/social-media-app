import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display the main heading', async ({ page }) => {
    const heading = page.locator('h1');
    await expect(heading).toContainText('AI-Powered Content');
    await expect(heading).toContainText('Operating System');
  });

  test('should display the navigation bar with logo', async ({ page }) => {
    const nav = page.locator('nav');
    await expect(nav).toBeVisible();
    await expect(nav.locator('text=Social Media Manager')).toBeVisible();
  });

  test('should have Log in and Get Started buttons in nav', async ({ page }) => {
    const nav = page.locator('nav');
    await expect(nav.getByRole('button', { name: /log in/i })).toBeVisible();
    await expect(nav.getByRole('button', { name: /get started/i })).toBeVisible();
  });

  test('should display the hero description', async ({ page }) => {
    await expect(page.locator('text=Research, ideate, create, repurpose')).toBeVisible();
    await expect(page.locator('text=Reduce content creation time by 80%')).toBeVisible();
  });

  test('should have CTA buttons in hero section', async ({ page }) => {
    await expect(page.getByRole('link', { name: /start free trial/i }).first()).toBeVisible();
    await expect(page.getByRole('link', { name: /watch demo/i })).toBeVisible();
  });

  test('should display all 4 feature cards', async ({ page }) => {
    await expect(page.locator('text=AI Content Creation')).toBeVisible();
    await expect(page.locator('text=Smart Scheduling')).toBeVisible();
    await expect(page.locator('text=Content Repurposing')).toBeVisible();
    await expect(page.locator('text=Analytics & Insights')).toBeVisible();
  });

  test('should display feature descriptions', async ({ page }) => {
    await expect(page.locator('text=Generate platform-specific content with AI')).toBeVisible();
    await expect(page.locator('text=Schedule posts across 5 platforms')).toBeVisible();
    await expect(page.locator('text=Turn one piece of content into 10')).toBeVisible();
    await expect(page.locator('text=Track performance across all platforms')).toBeVisible();
  });

  test('should display the CTA section', async ({ page }) => {
    await expect(page.locator('text=Ready to transform your content workflow?')).toBeVisible();
    await expect(page.locator('text=Join thousands of creators')).toBeVisible();
  });

  test('should display the footer', async ({ page }) => {
    await expect(page.locator('footer')).toBeVisible();
    await expect(page.locator('text=© 2026 Social Media Manager')).toBeVisible();
  });

  test('should navigate to login page via nav button', async ({ page }) => {
    await page.locator('nav').getByRole('button', { name: /log in/i }).click();
    await expect(page).toHaveURL(/\/auth\/login/);
  });

  test('should navigate to register page via nav button', async ({ page }) => {
    await page.locator('nav').getByRole('button', { name: /get started/i }).click();
    await expect(page).toHaveURL(/\/auth\/register/);
  });

  test('should navigate to register via hero CTA', async ({ page }) => {
    await page.getByRole('link', { name: /start free trial/i }).first().click();
    await expect(page).toHaveURL(/\/auth\/register/);
  });

  test('should navigate to login via Watch Demo button', async ({ page }) => {
    await page.getByRole('link', { name: /watch demo/i }).click();
    await expect(page).toHaveURL(/\/auth\/login/);
  });

  test('should have page title set correctly', async ({ page }) => {
    await expect(page).toHaveTitle(/Social Media Manager/);
  });

  // DESIGN SYSTEM: Feature cards should have consistent border radius
  test('feature cards should have consistent border radius', async ({ page }) => {
    const cards = page.locator('.rounded-xl');
    const count = await cards.count();
    expect(count).toBeGreaterThan(0);
    const radii: string[] = [];
    for (let i = 0; i < count; i++) {
      const radius = await cards.nth(i).evaluate(el =>
        getComputedStyle(el).borderRadius
      );
      radii.push(radius);
    }
    // All cards should have same radius
    expect(new Set(radii).size).toBe(1);
  });

  // DESIGN SYSTEM: No hardcoded hex colors — should use semantic tokens
  test('should not use hardcoded hex colors in CSS classes', async ({ page }) => {
    const html = await page.content();
    // Check for inline hex colors in style attributes (not in Tailwind classes)
    const inlineHexMatches = html.match(/style="[^"]*#[0-9a-fA-F]{3,8}/g);
    expect(inlineHexMatches).toBeNull();
  });

  // DESIGN SYSTEM: Proper heading hierarchy
  test('should have proper heading hierarchy', async ({ page }) => {
    const headings = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('h1, h2, h3, h4'))
        .map(h => parseInt(h.tagName.charAt(1)));
    });
    expect(headings.length).toBeGreaterThan(0);
    // First heading should be h1
    expect(headings[0]).toBe(1);
    // Check hierarchy is not jumping levels (e.g., h1 -> h3)
    for (let i = 1; i < headings.length; i++) {
      expect(headings[i]).toBeLessThanOrEqual(headings[i - 1] + 1);
    }
  });
});
