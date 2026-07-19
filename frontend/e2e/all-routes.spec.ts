import { test, expect } from '@playwright/test';

const ALL_ROUTES = [
  // Public routes
  { path: '/', name: 'Landing Page', auth: false },
  { path: '/auth/login', name: 'Login', auth: false },
  { path: '/auth/register', name: 'Register', auth: false },
  // Protected dashboard routes
  { path: '/dashboard', name: 'Dashboard', auth: true },
  { path: '/dashboard/content-studio', name: 'Content Studio', auth: true },
  { path: '/dashboard/research', name: 'Research', auth: true },
  { path: '/dashboard/calendar', name: 'Calendar', auth: true },
  { path: '/dashboard/repurpose', name: 'Repurpose', auth: true },
  { path: '/dashboard/media', name: 'Media', auth: true },
  { path: '/dashboard/inbox', name: 'Inbox', auth: true },
  { path: '/dashboard/listening', name: 'Listening', auth: true },
  { path: '/dashboard/ai-assistant', name: 'AI Assistant', auth: true },
  { path: '/dashboard/recommendations', name: 'Recommendations', auth: true },
  { path: '/dashboard/analytics', name: 'Analytics', auth: true },
  { path: '/dashboard/ads', name: 'Ads', auth: true },
  { path: '/dashboard/reports', name: 'Reports', auth: true },
  { path: '/dashboard/competitors', name: 'Competitors', auth: true },
  { path: '/dashboard/team', name: 'Team', auth: true },
  { path: '/dashboard/connections', name: 'Connections', auth: true },
  { path: '/dashboard/approvals', name: 'Approvals', auth: true },
  { path: '/dashboard/tasks', name: 'Tasks', auth: true },
  { path: '/dashboard/automation', name: 'Automation', auth: true },
  { path: '/dashboard/advocacy', name: 'Advocacy', auth: true },
  { path: '/dashboard/billing', name: 'Billing', auth: true },
  { path: '/dashboard/security', name: 'Security', auth: true },
  { path: '/dashboard/settings', name: 'Settings', auth: true },
];

test.describe('All Routes - Smoke Test', () => {
  for (const route of ALL_ROUTES) {
    test(`${route.name} (${route.path}) should load without 500 error`, async ({ page }) => {
      const response = await page.goto(route.path);
      expect(response).toBeTruthy();
      expect(response?.status()).toBeLessThan(500);
    });
  }
});

test.describe('All Protected Routes - Auth Guard', () => {
  const protectedRoutes = ALL_ROUTES.filter(r => r.auth);

  for (const route of protectedRoutes) {
    test(`${route.name} should redirect to login`, async ({ page }) => {
      await page.goto(route.path);
      await expect(page).toHaveURL(/\/auth\/login/, { timeout: 10000 });
    });
  }
});

test.describe('Public Routes - Should NOT Redirect to Login', () => {
  const publicRoutes = ALL_ROUTES.filter(r => !r.auth && r.path !== '/auth/login');

  for (const route of publicRoutes) {
    test(`${route.name} should stay on ${route.path}`, async ({ page }) => {
      await page.goto(route.path);
      // Should NOT redirect to /auth/login
      const url = new URL(page.url());
      expect(url.pathname).toBe(route.path);
    });
  }
});
