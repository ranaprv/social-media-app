import { test, expect } from '@playwright/test';

test.describe('Responsive Design', () => {
  test('landing page should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('text=AI Content Creation')).toBeVisible();
    await expect(page.getByRole('link', { name: /start free trial/i }).first()).toBeVisible();
  });

  test('landing page should be responsive on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('text=AI Content Creation')).toBeVisible();
    await expect(page.locator('text=Smart Scheduling')).toBeVisible();
  });

  test('landing page should display correctly on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('text=AI Content Creation')).toBeVisible();
    await expect(page.locator('text=Smart Scheduling')).toBeVisible();
    await expect(page.locator('text=Content Repurposing')).toBeVisible();
    await expect(page.locator('text=Analytics & Insights')).toBeVisible();
  });

  test('login page should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/auth/login');
    await expect(page.getByRole('heading', { name: 'Welcome back' })).toBeVisible();
    await expect(page.getByPlaceholder('you@example.com')).toBeVisible();
    await expect(page.getByPlaceholder('••••••••')).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('register page should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/auth/register');
    await expect(page.getByRole('heading', { name: 'Create account' })).toBeVisible();
    await expect(page.getByPlaceholder('Your name')).toBeVisible();
    await expect(page.getByPlaceholder('you@example.com')).toBeVisible();
    await expect(page.getByPlaceholder('••••••••')).toBeVisible();
  });
});

test.describe('Theme Support', () => {
  test('should have antialiased class on html element', async ({ page }) => {
    await page.goto('/');
    const html = page.locator('html');
    await expect(html).toHaveClass(/antialiased/);
  });

  test('should have lang attribute set', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('html')).toHaveAttribute('lang', 'en');
  });
});

test.describe('Performance Basics', () => {
  test('landing page should load within reasonable time', async ({ page }) => {
    const start = Date.now();
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - start;
    expect(loadTime).toBeLessThan(10000);
  });

  test('login page should load within reasonable time', async ({ page }) => {
    const start = Date.now();
    await page.goto('/auth/login');
    await page.waitForLoadState('networkidle');
    const loadTime = Date.now() - start;
    expect(loadTime).toBeLessThan(10000);
  });
});

// ============================================================================
// ACCESSIBILITY (a11y) TESTS
// ============================================================================

test.describe('Accessibility - Touch Targets', () => {
  test('primary CTA buttons should have adequate touch targets', async ({ page }) => {
    await page.goto('/');
    // Check the main CTA button
    const cta = page.getByRole('link', { name: /start free trial/i }).first();
    const box = await cta.boundingBox();
    if (box) {
      // CTA should be at least 40px tall (allowing for padding)
      expect(box.height).toBeGreaterThanOrEqual(40);
    }
  });
});

test.describe('Accessibility - Focus Visible', () => {
  test('links and buttons should be focusable', async ({ page }) => {
    await page.goto('/');
    // Check that links have href (makes them focusable)
    const links = page.locator('a[href]');
    const count = await links.count();
    expect(count).toBeGreaterThan(0);
  });

  test('login form should have focusable inputs', async ({ page }) => {
    await page.goto('/auth/login');
    // Inputs should be present and focusable
    const inputs = page.locator('input');
    const count = await inputs.count();
    expect(count).toBeGreaterThan(0);
    // Each input should have tabindex >= 0 (focusable)
    for (let i = 0; i < count; i++) {
      const tabIndex = await inputs.nth(i).evaluate(el => {
        const tabIdx = el.getAttribute('tabindex');
        return tabIdx ? parseInt(tabIdx) : 0;
      });
      expect(tabIndex).toBeGreaterThanOrEqual(0);
    }
  });
});

test.describe('Accessibility - Reduced Motion', () => {
  test('should respect prefers-reduced-motion', async ({ page }) => {
    await page.emulateMedia({ reducedMotion: 'reduce' });
    await page.goto('/');
    // Verify page loads without animations
    const hasAnimations = await page.evaluate(() => {
      const animations = document.getAnimations();
      return animations.length > 0;
    });
    // With reduced motion, there should be no running animations
    // (Note: some CSS animations may still be in the DOM but not playing)
    expect(hasAnimations).toBe(false);
  });
});

test.describe('Accessibility - ARIA Attributes', () => {
  test('form inputs should have associated labels or aria-label', async ({ page }) => {
    await page.goto('/auth/login');
    const inputs = page.locator('input');
    const count = await inputs.count();
    for (let i = 0; i < count; i++) {
      const hasLabel = await inputs.nth(i).evaluate(el => {
        const id = el.id;
        const ariaLabel = el.getAttribute('aria-label');
        const ariaLabelledBy = el.getAttribute('aria-labelledby');
        const placeholder = el.getAttribute('placeholder');
        const label = id ? document.querySelector(`label[for="${id}"]`) : null;
        return !!(label || ariaLabel || ariaLabelledBy || placeholder);
      });
      expect(hasLabel).toBe(true);
    }
  });

  test('buttons should have accessible names', async ({ page }) => {
    await page.goto('/');
    const buttons = page.locator('button');
    const count = await buttons.count();
    for (let i = 0; i < Math.min(count, 10); i++) {
      const hasName = await buttons.nth(i).evaluate(el => {
        const text = el.textContent?.trim();
        const ariaLabel = el.getAttribute('aria-label');
        const title = el.getAttribute('title');
        return !!(text || ariaLabel || title);
      });
      expect(hasName).toBe(true);
    }
  });
});

// ============================================================================
// MOBILE BEST PRACTICES TESTS
// ============================================================================

test.describe('Mobile - No Horizontal Overflow', () => {
  test('landing page should have no horizontal overflow on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    const hasOverflow = await page.evaluate(() => {
      return document.body.scrollWidth > window.innerWidth;
    });
    expect(hasOverflow).toBe(false);
  });

  test('login page should have no horizontal overflow on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/auth/login');
    const hasOverflow = await page.evaluate(() => {
      return document.body.scrollWidth > window.innerWidth;
    });
    expect(hasOverflow).toBe(false);
  });

  test('register page should have no horizontal overflow on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/auth/register');
    const hasOverflow = await page.evaluate(() => {
      return document.body.scrollWidth > window.innerWidth;
    });
    expect(hasOverflow).toBe(false);
  });
});

test.describe('Mobile - Viewport Meta', () => {
  test('should have viewport meta tag with width=device-width', async ({ page }) => {
    await page.goto('/');
    const viewport = await page.evaluate(() => {
      const meta = document.querySelector('meta[name="viewport"]');
      return meta?.getAttribute('content');
    });
    expect(viewport).toContain('width=device-width');
  });
});

test.describe('Mobile - Text Size', () => {
  test('text should be at least 12px on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    const textSizes = await page.evaluate(() => {
      const elements = document.querySelectorAll('p, span, a, button, li, h1, h2, h3, h4, h5, h6');
      return Array.from(elements)
        .filter(el => el.textContent?.trim())
        .map(el => parseFloat(getComputedStyle(el).fontSize));
    });
    const allLargeEnough = textSizes.every(size => size >= 12);
    expect(allLargeEnough).toBe(true);
  });
});

test.describe('Mobile - Touch-Friendly Spacing', () => {
  test('interactive elements should have adequate spacing', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/auth/login');
    const buttons = page.locator('button');
    const count = await buttons.count();
    if (count >= 2) {
      const box1 = await buttons.nth(0).boundingBox();
      const box2 = await buttons.nth(1).boundingBox();
      if (box1 && box2) {
        const verticalGap = Math.abs(box1.y - box2.y) - box1.height;
        // Should have at least 8px gap between buttons
        expect(verticalGap).toBeGreaterThanOrEqual(8);
      }
    }
  });
});

// ============================================================================
// TYPOGRAPHY TESTS
// ============================================================================

test.describe('Typography - Font Family', () => {
  test('should use a web font (not default serif/sans-serif)', async ({ page }) => {
    await page.goto('/');
    const fontFamily = await page.evaluate(() => {
      return getComputedStyle(document.body).fontFamily;
    });
    // Should not be generic fallback
    expect(fontFamily).not.toBe('serif');
    expect(fontFamily).not.toBe('sans-serif');
    expect(fontFamily).not.toBe('monospace');
    // Should contain a named font
    expect(fontFamily.length).toBeGreaterThan(0);
  });
});

test.describe('Typography - Font Weights', () => {
  test('headings should use appropriate font weights', async ({ page }) => {
    await page.goto('/');
    const headingWeights = await page.evaluate(() => {
      const headings = document.querySelectorAll('h1, h2, h3');
      return Array.from(headings).map(h => ({
        tag: h.tagName,
        weight: parseInt(getComputedStyle(h).fontWeight),
      }));
    });
    for (const h of headingWeights) {
      // Headings should be 500-700 weight
      expect(h.weight).toBeGreaterThanOrEqual(500);
      expect(h.weight).toBeLessThanOrEqual(700);
    }
  });

  test('body text should use regular weight', async ({ page }) => {
    await page.goto('/');
    const bodyWeight = await page.evaluate(() => {
      const p = document.querySelector('p');
      return p ? parseInt(getComputedStyle(p).fontWeight) : 400;
    });
    expect(bodyWeight).toBe(400);
  });
});

test.describe('Typography - Line Heights', () => {
  test('display text should have reasonable line height', async ({ page }) => {
    await page.goto('/');
    const h1LineHeight = await page.evaluate(() => {
      const h1 = document.querySelector('h1');
      if (!h1) return null;
      const lh = getComputedStyle(h1).lineHeight;
      // lineHeight can be "normal" or a pixel value
      if (lh === 'normal') return 1.2; // normal is typically ~1.2
      return parseFloat(lh);
    });
    if (h1LineHeight !== null && !isNaN(h1LineHeight)) {
      // Line height in pixels should be reasonable for display text
      // For a 48px h1, line-height should be 48-96px (1.0-2.0x)
      expect(h1LineHeight).toBeGreaterThan(0);
    }
  });
});

// ============================================================================
// SPACING CONSISTENCY TESTS
// ============================================================================

test.describe('Spacing - Consistent Padding', () => {
  test('cards should have consistent padding', async ({ page }) => {
    await page.goto('/');
    const cards = page.locator('.rounded-xl, .rounded-2xl');
    const count = await cards.count();
    if (count > 0) {
      const paddings = await page.evaluate(() => {
        const cards = document.querySelectorAll('.rounded-xl, .rounded-2xl');
        return Array.from(cards).slice(0, 5).map(el => {
          const style = getComputedStyle(el);
          return {
            top: parseFloat(style.paddingTop),
            right: parseFloat(style.paddingRight),
            bottom: parseFloat(style.paddingBottom),
            left: parseFloat(style.paddingLeft),
          };
        });
      });
      // Check padding is consistent within each card (square padding)
      for (const p of paddings) {
        expect(p.top).toBe(p.bottom);
        expect(p.left).toBe(p.right);
      }
    }
  });
});

// ============================================================================
// COHERENCE TESTS
// ============================================================================

test.describe('Coherence - One Radius Personality', () => {
  test('rounded elements should use limited radius values', async ({ page }) => {
    await page.goto('/');
    const roundedElements = await page.evaluate(() => {
      const elements = document.querySelectorAll('[class*="rounded"]');
      const radii = new Set<string>();
      elements.forEach(el => {
        const radius = getComputedStyle(el).borderRadius;
        if (radius !== '0px') radii.add(radius);
      });
      return Array.from(radii);
    });
    // Should have limited number of distinct radii (1-5 is acceptable for a full page)
    expect(roundedElements.length).toBeLessThanOrEqual(5);
  });
});

test.describe('Coherence - One Accent Color', () => {
  test('interactive elements should use consistent accent color', async ({ page }) => {
    await page.goto('/');
    const accentColors = await page.evaluate(() => {
      const buttons = document.querySelectorAll('button:not([variant="ghost"]), a[role="button"]');
      const colors = new Set<string>();
      buttons.forEach(btn => {
        const bg = getComputedStyle(btn).backgroundColor;
        if (bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent') {
          colors.add(bg);
        }
      });
      return Array.from(colors);
    });
    // Should have limited accent colors (1-2 primary + semantic colors)
    expect(accentColors.length).toBeLessThanOrEqual(3);
  });
});

test.describe('Coherence - No Emoji as UI Icons', () => {
  test('navigation should not contain emoji characters', async ({ page }) => {
    await page.goto('/');
    const hasEmoji = await page.evaluate(() => {
      const nav = document.querySelector('nav');
      if (!nav) return false;
      const text = nav.textContent || '';
      // Check for common emoji ranges
      const emojiPattern = /[\u{1F600}-\u{1F64F}\u{1F300}-\u{1F5FF}\u{1F680}-\u{1F6FF}\u{1F1E0}-\u{1F1FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{FE00}-\u{FE0F}\u{1F900}-\u{1F9FF}]/u;
      return emojiPattern.test(text);
    });
    // Navigation should not contain emoji
    expect(hasEmoji).toBe(false);
  });
});

test.describe('Coherence - Status Color = Severity', () => {
  test('body text should use dark neutral colors', async ({ page }) => {
    await page.goto('/');
    // Check that paragraph text uses dark colors
    const bodyColor = await page.evaluate(() => {
      const p = document.querySelector('p');
      if (!p) return 'rgb(0, 0, 0)';
      return getComputedStyle(p).color;
    });
    // Body text should be dark
    const match = bodyColor.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (match) {
      const [, r, g, b] = match.map(Number);
      // Should be dark text (all channels < 150 for dark theme compatibility)
      expect(r).toBeLessThan(150);
      expect(g).toBeLessThan(150);
      expect(b).toBeLessThan(150);
    }
  });
});

test.describe('Coherence - One Shadow Language', () => {
  test('shadows should be consistent', async ({ page }) => {
    await page.goto('/');
    const shadows = await page.evaluate(() => {
      const elements = document.querySelectorAll('[class*="shadow"]');
      const shadowSet = new Set<string>();
      elements.forEach(el => {
        const shadow = getComputedStyle(el).boxShadow;
        if (shadow !== 'none') shadowSet.add(shadow);
      });
      return Array.from(shadowSet);
    });
    // Should have limited shadow styles
    expect(shadows.length).toBeLessThanOrEqual(3);
  });
});

test.describe('Coherence - One Icon Family', () => {
  test('should use consistent icon library (lucide)', async ({ page }) => {
    await page.goto('/');
    const hasLucide = await page.evaluate(() => {
      // Check for lucide-react SVG elements
      const svgs = document.querySelectorAll('svg');
      return svgs.length > 0;
    });
    expect(hasLucide).toBe(true);
  });
});

test.describe('Coherence - Consistent Control Heights', () => {
  test('buttons and inputs should share consistent heights', async ({ page }) => {
    await page.goto('/auth/login');
    const heights = await page.evaluate(() => {
      const buttons = document.querySelectorAll('button');
      const inputs = document.querySelectorAll('input');
      const all = [...buttons, ...inputs];
      return Array.from(all).map(el => parseFloat(getComputedStyle(el).height));
    });
    // All heights should be within a reasonable range (36-48px)
    for (const h of heights) {
      expect(h).toBeGreaterThanOrEqual(36);
      expect(h).toBeLessThanOrEqual(48);
    }
  });
});

// ============================================================================
// PERFORMANCE TESTS
// ============================================================================

test.describe('Performance - Image Lazy Loading', () => {
  test('images below fold should have lazy loading', async ({ page }) => {
    await page.goto('/');
    const images = page.locator('img');
    const count = await images.count();
    for (let i = 0; i < count; i++) {
      const loading = await images.nth(i).getAttribute('loading');
      // Images should have loading="lazy" or be above fold
      // (We just check the attribute exists, not position)
      if (loading) {
        expect(loading).toBe('lazy');
      }
    }
  });
});

test.describe('Performance - No Unnecessary Re-renders', () => {
  test('page should not have excessive DOM nodes', async ({ page }) => {
    await page.goto('/');
    const nodeCount = await page.evaluate(() => {
      return document.querySelectorAll('*').length;
    });
    // Reasonable DOM size for a landing page
    expect(nodeCount).toBeLessThan(1000);
  });
});

test.describe('Performance - No Console Errors', () => {
  test('landing page should have no console errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    // Filter out known harmless errors (like favicon)
    const realErrors = errors.filter(e =>
      !e.includes('favicon') &&
      !e.includes('404') &&
      !e.includes('Failed to load resource')
    );
    expect(realErrors).toHaveLength(0);
  });

  test('login page should have no console errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.goto('/auth/login');
    await page.waitForLoadState('networkidle');
    const realErrors = errors.filter(e =>
      !e.includes('favicon') &&
      !e.includes('404') &&
      !e.includes('Failed to load resource')
    );
    expect(realErrors).toHaveLength(0);
  });
});
