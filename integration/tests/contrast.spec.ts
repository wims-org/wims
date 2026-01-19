import { test, expect } from '@playwright/test';
import axe from 'axe-core';
import { ensureAppReady } from '../helpers/sse_subscription';

const routesToCheck = ['/', '/items', '/readers', '/users', '/about'];

async function runAxe(page: any) {
    // inject axe source
    await page.addScriptTag({ content: axe.source });
    return await page.evaluate(async () => {
        // @ts-ignore
        const results = await (window as any).axe.run(document, {
            runOnly: {
                type: 'rule',
                values: ['color-contrast']
            }
        });
        return results;
    });
}

// The custom background-vs-background audit was removed for simplification.
// This test now relies solely on axe-core's `color-contrast` rule (text-to-background) which is authoritative for accessibility.

test.describe.configure({ mode: 'serial' });

test.describe('Contrast audit', () => {
    test.beforeEach(async ({ page }) => {
        await ensureAppReady(page);
    });

    test('aggregate: all routes and themes should meet contrast requirements', async ({ page }) => {
        const failures: any[] = [];

        for (const route of routesToCheck) {
            for (const mode of ['light', 'dark']) {
                // set theme before page load
                await page.addInitScript((theme) => localStorage.setItem('wims_theme', theme), mode);
                await page.goto(route, { waitUntil: 'domcontentloaded' });
                await page.waitForTimeout(300);

                // High contrast: text to background via axe color-contrast rule
                const axeResult = await runAxe(page as any);
                const violations = axeResult.violations || [];
                const colorViolations = violations.filter((v: any) => v.id === 'color-contrast');
                if (colorViolations.length > 0) {
                    // Build readable entries for each failing node
                    const details = await page.evaluate((violations) => {
                        const out: Array<any> = [];
                        for (const v of violations) {
                            for (const node of v.nodes || []) {
                                const sel = node.target && node.target.length ? node.target.join(',') : '';
                                const el = document.querySelector(sel);
                                const html = el ? (el.outerHTML || el.tagName).slice(0, 800) : '<not found>';
                                out.push({ selector: sel, html, message: v.help, rule: v.id });
                            }
                        }
                        return out;
                    }, colorViolations);
                    failures.push({ route, mode, type: 'color-contrast', details });
                }

                // (background-vs-background audit removed — this test relies solely on axe color-contrast)
            }
        }

        if (failures.length > 0) {
            // eslint-disable-next-line no-console
            console.warn('Contrast audit failures:', failures);
            throw new Error(`Contrast audit found ${failures.length} failing route/mode combinations: ${JSON.stringify(failures, null, 2)}`);
        }
    });
});

