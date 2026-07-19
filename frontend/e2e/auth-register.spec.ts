import { test, expect } from '@playwright/test';

test.describe('Register Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/auth/register');
  });

  test('should display the registration form', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Create account' })).toBeVisible();
    await expect(page.locator('text=Start creating with Social Media Manager')).toBeVisible();
  });

  test('should display name, email, and password fields', async ({ page }) => {
    await expect(page.getByPlaceholder('Your name')).toBeVisible();
    await expect(page.getByPlaceholder('you@example.com')).toBeVisible();
    await expect(page.getByPlaceholder('••••••••')).toBeVisible();
  });

  test('should have Create Account button', async ({ page }) => {
    await expect(page.getByRole('button', { name: /create account/i })).toBeVisible();
  });

  test('should have Google and GitHub OAuth buttons', async ({ page }) => {
    await expect(page.getByRole('button', { name: 'Google' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'GitHub' })).toBeVisible();
  });

  test('should display "or continue with" divider', async ({ page }) => {
    await expect(page.locator('text=or continue with')).toBeVisible();
  });

  test('should have link to login page', async ({ page }) => {
    const loginLink = page.getByRole('link', { name: /sign in/i });
    await expect(loginLink).toBeVisible();
    await loginLink.click();
    await expect(page).toHaveURL(/\/auth\/login/);
  });

  test('should have required attributes on fields', async ({ page }) => {
    await expect(page.getByPlaceholder('you@example.com')).toHaveAttribute('required', '');
    await expect(page.getByPlaceholder('••••••••')).toHaveAttribute('required', '');
  });

  test('should have minLength on password field', async ({ page }) => {
    await expect(page.getByPlaceholder('••••••••')).toHaveAttribute('minlength', '8');
  });

  test('should allow typing in name field', async ({ page }) => {
    const nameInput = page.getByPlaceholder('Your name');
    await nameInput.click();
    await nameInput.pressSequentially('John Doe');
    await expect(nameInput).toHaveValue('John Doe');
  });

  test('should allow typing in email field', async ({ page }) => {
    const emailInput = page.getByPlaceholder('you@example.com');
    await emailInput.fill('john@example.com');
    await expect(emailInput).toHaveValue('john@example.com');
  });

  test('should allow typing in password field', async ({ page }) => {
    const passwordInput = page.getByPlaceholder('••••••••');
    await passwordInput.fill('securepassword');
    await expect(passwordInput).toHaveValue('securepassword');
  });

  test('should have password field with correct type', async ({ page }) => {
    await expect(page.getByPlaceholder('••••••••')).toHaveAttribute('type', 'password');
  });

  test('should have email field with correct type', async ({ page }) => {
    await expect(page.getByPlaceholder('you@example.com')).toHaveAttribute('type', 'email');
  });

  test('should display the Zap icon logo', async ({ page }) => {
    const logoContainer = page.locator('.rounded-full.bg-primary\\/10');
    await expect(logoContainer).toBeVisible();
  });

  test('should attempt registration and show backend error', async ({ page }) => {
    await page.getByPlaceholder('Your name').fill('Test User');
    await page.getByPlaceholder('you@example.com').fill('test@example.com');
    await page.getByPlaceholder('••••••••').fill('password123');
    await page.getByRole('button', { name: /create account/i }).click();
    // Backend not running, expect error
    await expect(page.locator('.text-destructive')).toBeVisible({ timeout: 10000 });
  });
});

// ============================================================================
// ACCESSIBILITY TESTS
// ============================================================================

test.describe('Register - Accessibility', () => {
  test('form should have proper label associations', async ({ page }) => {
    await page.goto('/auth/register');
    const inputs = page.locator('input');
    const count = await inputs.count();
    for (let i = 0; i < count; i++) {
      const hasAssociation = await inputs.nth(i).evaluate(el => {
        const id = el.id;
        const ariaLabel = el.getAttribute('aria-label');
        const ariaLabelledBy = el.getAttribute('aria-labelledby');
        const placeholder = el.getAttribute('placeholder');
        const label = id ? document.querySelector(`label[for="${id}"]`) : null;
        const parentLabel = el.closest('label');
        return !!(label || parentLabel || ariaLabel || ariaLabelledBy || placeholder);
      });
      expect(hasAssociation).toBe(true);
    }
  });

  test('error messages should be visible and descriptive', async ({ page }) => {
    await page.goto('/auth/register');
    // Fill form and submit to trigger error
    await page.getByPlaceholder('Your name').fill('Test');
    await page.getByPlaceholder('you@example.com').fill('test@test.com');
    await page.getByPlaceholder('••••••••').fill('password123');
    await page.getByRole('button', { name: /create account/i }).click();
    // Wait for error
    await expect(page.locator('.text-destructive')).toBeVisible({ timeout: 10000 });
    // Error should contain meaningful text
    const errorText = await page.locator('.text-destructive').textContent();
    expect(errorText?.length).toBeGreaterThan(0);
  });

  test('password requirements should be accessible', async ({ page }) => {
    await page.goto('/auth/register');
    // Password field should indicate minimum length
    const hasMinLength = await page.getByPlaceholder('••••••••').getAttribute('minlength');
    expect(hasMinLength).toBe('8');
  });
});

// ============================================================================
// DESIGN SYSTEM TESTS
// ============================================================================

test.describe('Register - Design System', () => {
  test('form should be contained in a styled card', async ({ page }) => {
    await page.goto('/auth/register');
    const formParent = page.locator('form').locator('..');
    const hasBorderRadius = await formParent.evaluate(el => {
      const radius = getComputedStyle(el).borderRadius;
      return parseFloat(radius) > 0;
    });
    const formGrandparent = formParent.locator('..');
    const gpHasRadius = await formGrandparent.evaluate(el => {
      const radius = getComputedStyle(el).borderRadius;
      return parseFloat(radius) > 0;
    });
    expect(hasBorderRadius || gpHasRadius).toBe(true);
  });

  test('all inputs should have reasonable height', async ({ page }) => {
    await page.goto('/auth/register');
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
    await page.goto('/auth/register');
    const button = page.getByRole('button', { name: /create account/i });
    await expect(button).toBeVisible();
    const text = await button.textContent();
    expect(text).toContain('Create Account');
  });

  test('no hardcoded colors in inline styles', async ({ page }) => {
    await page.goto('/auth/register');
    const html = await page.content();
    const inlineHexMatches = html.match(/style="[^"]*#[0-9a-fA-F]{3,8}/g);
    expect(inlineHexMatches).toBeNull();
  });
});
