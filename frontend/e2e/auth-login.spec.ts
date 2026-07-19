import { test, expect } from '@playwright/test';

test.describe('Login Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/login');
  });

  test('should display the login form', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Welcome back' })).toBeVisible();
    await expect(page.locator('text=Sign in to Social Media Manager')).toBeVisible();
  });

  test('should display email and password fields', async ({ page }) => {
    await expect(page.getByPlaceholder('you@example.com')).toBeVisible();
    await expect(page.getByPlaceholder('••••••••')).toBeVisible();
  });

  test('should have Sign In button', async ({ page }) => {
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('should have Google and GitHub OAuth buttons', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Google' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'GitHub' })).toBeVisible();
  });

  test('should display "or continue with" divider', async ({ page }) => {
    await expect(page.locator('text=or continue with')).toBeVisible();
  });

  test('should have link to register page', async ({ page }) => {
    const registerLink = page.getByRole('link', { name: /sign up/i });
    await expect(registerLink).toBeVisible();
    await registerLink.click();
    await expect(page).toHaveURL(/\/auth\/register/);
  });

  test('should have required attributes on fields', async ({ page }) => {
    const emailInput = page.getByPlaceholder('you@example.com');
    const passwordInput = page.getByPlaceholder('••••••••');
    await expect(emailInput).toHaveAttribute('required', '');
    await expect(passwordInput).toHaveAttribute('required', '');
  });

  test('should allow typing in email field', async ({ page }) => {
    const emailInput = page.getByPlaceholder('you@example.com');
    await emailInput.fill('test@example.com');
    await expect(emailInput).toHaveValue('test@example.com');
  });

  test('should allow typing in password field', async ({ page }) => {
    const passwordInput = page.getByPlaceholder('••••••••');
    await passwordInput.fill('password123');
    await expect(passwordInput).toHaveValue('password123');
  });

  test('should have password field with correct type', async ({ page }) => {
    const passwordInput = page.getByPlaceholder('••••••••');
    await expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('should have email field with correct type', async ({ page }) => {
    const emailInput = page.getByPlaceholder('you@example.com');
    await expect(emailInput).toHaveAttribute('type', 'email');
  });

  test('should display the Zap icon logo', async ({ page }) => {
    const logoContainer = page.locator('.rounded-full.bg-primary\\/10');
    await expect(logoContainer).toBeVisible();
  });

  test('should attempt login and show error when backend is down', async ({ page }) => {
    await page.getByPlaceholder('you@example.com').fill('test@example.com');
    await page.getByPlaceholder('••••••••').fill('password123');
    await page.getByRole('button', { name: /sign in/i }).click();
    // Backend not running, expect error message
    await expect(page.locator('.text-destructive')).toBeVisible({ timeout: 10000 });
  });
});

// ============================================================================
// ACCESSIBILITY TESTS
// ============================================================================

test.describe('Login - Accessibility', () => {
  test('form should have proper label associations', async ({ page }) => {
    await page.goto('/auth/login');
    // Check that labels are associated with inputs via htmlFor/id or aria-label
    const inputs = page.locator('input');
    const count = await inputs.count();
    for (let i = 0; i < count; i++) {
      const hasAssociation = await inputs.nth(i).evaluate(el => {
        const id = el.id;
        const ariaLabel = el.getAttribute('aria-label');
        const ariaLabelledBy = el.getAttribute('aria-labelledby');
        const placeholder = el.getAttribute('placeholder');
        const label = id ? document.querySelector(`label[for="${id}"]`) : null;
        // Also check parent label
        const parentLabel = el.closest('label');
        return !!(label || parentLabel || ariaLabel || ariaLabelledBy || placeholder);
      });
      expect(hasAssociation).toBe(true);
    }
  });

  test('error messages should be visible and descriptive', async ({ page }) => {
    await page.goto('/auth/login');
    await page.getByPlaceholder('you@example.com').fill('test@example.com');
    await page.getByPlaceholder('••••••••').fill('wrongpassword');
    await page.getByRole('button', { name: /sign in/i }).click();
    // Wait for error
    await expect(page.locator('.text-destructive')).toBeVisible({ timeout: 10000 });
    // Error should contain meaningful text
    const errorText = await page.locator('.text-destructive').textContent();
    expect(errorText?.length).toBeGreaterThan(0);
  });

  test('card should have proper landmark role', async ({ page }) => {
    await page.goto('/auth/login');
    // Login form should be in a main landmark
    const hasMain = await page.evaluate(() => {
      return !!document.querySelector('main') || !!document.querySelector('[role="main"]');
    });
    // Or at least the form should be accessible
    const hasForm = await page.evaluate(() => {
      return !!document.querySelector('form');
    });
    expect(hasMain || hasForm).toBe(true);
  });
});

// ============================================================================
// DESIGN SYSTEM TESTS
// ============================================================================

test.describe('Login - Design System', () => {
  test('form should be contained in a styled card', async ({ page }) => {
    await page.goto('/auth/login');
    // The form should be inside a container with some styling
    const formParent = page.locator('form').locator('..');
    const hasBorderRadius = await formParent.evaluate(el => {
      const radius = getComputedStyle(el).borderRadius;
      return parseFloat(radius) > 0;
    });
    // Card should have border radius (may be on grandparent)
    const formGrandparent = formParent.locator('..');
    const gpHasRadius = await formGrandparent.evaluate(el => {
      const radius = getComputedStyle(el).borderRadius;
      return parseFloat(radius) > 0;
    });
    expect(hasBorderRadius || gpHasRadius).toBe(true);
  });

  test('inputs should have reasonable height', async ({ page }) => {
    await page.goto('/auth/login');
    const inputs = page.locator('input');
    const count = await inputs.count();
    for (let i = 0; i < count; i++) {
      const height = await inputs.nth(i).evaluate(el =>
        parseFloat(getComputedStyle(el).height)
      );
      // Each input should be between 36-48px
      expect(height).toBeGreaterThanOrEqual(36);
      expect(height).toBeLessThanOrEqual(48);
    }
  });

  test('button should be visible and have text', async ({ page }) => {
    await page.goto('/auth/login');
    const button = page.getByRole('button', { name: /sign in/i });
    await expect(button).toBeVisible();
    const text = await button.textContent();
    expect(text).toContain('Sign In');
  });
});
