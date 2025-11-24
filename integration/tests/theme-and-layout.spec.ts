import { test, expect } from '@playwright/test';
import { ensureAppReady } from '../helpers/sse_subscription';

test.describe('Layout', () => {
    test('mobile layout shows offcanvas menu and responsive components', async ({ page }) => {
        // Emulate a small screen
        await page.goto('/');
        await page.waitForLoadState("domcontentloaded");
        await page.setViewportSize({ width: 390, height: 844 });

        // Wait for the navbar toggle to appear
        const toggle = page.locator('[aria-label="Open menu"]');
        await toggle.waitFor({ timeout: 10000 });

        // The navbar toggle should be visible on mobile
        await expect(toggle).toBeVisible();
        await toggle.click();

        // Now the offcanvas should be visible
        const offcanvas = page.locator('#offcanvasMenu');
        await expect(offcanvas).toBeVisible();

        // Check that theme toggle exists inside offcanvas
        const themeToggle = offcanvas.getByLabel('Toggle dark theme');
        await expect(themeToggle).toBeVisible();
    });
});
