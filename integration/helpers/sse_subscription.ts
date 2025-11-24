import { expect, type Page, APIResponse } from "playwright/test";

export async function connectToReader(page: Page, reader_id: string): Promise<string> {
  await page.goto("/");
  await page.waitForLoadState("domcontentloaded");
  await page.goto("/readers");
  await page.getByTestId("reader-list").waitFor({ timeout: 10000 });
  const isLargeViewport = await page.evaluate(() => window.innerWidth > 1024);
  const isMobileViewport = await page.evaluate(() => window.innerWidth < 768);

  const connectionState = isLargeViewport
    ? page.locator('[data-testid="sse-connection-state-lg"]')
    : page.locator('[data-testid="sse-connection-state"]');

  const hasConnectionState = (await connectionState.count()) > 0;
  if (hasConnectionState && !isMobileViewport) {
    await expect(connectionState.first()).toBeVisible({ timeout: 5000 });
  }

  // already connected, return early
  if (hasConnectionState) {
    const csText = (await connectionState.first().textContent()) || "";
    if (csText.includes(reader_id)) {
      return reader_id;
    }
  }

  let readerItem = page.getByTestId("reader-item").filter({ hasText: reader_id }).first();
  if ((await readerItem.count()) === 0) {
    await page.getByRole("textbox", { name: "Reader Name" }).fill("Reader-" + reader_id);
    await page.getByRole("textbox", { name: "Reader ID" }).fill(reader_id);
    await page.getByRole("button", { name: "Add Reader" }).click();
    await page.waitForTimeout(300);
    readerItem = page.getByTestId("reader-item").filter({ hasText: reader_id }).first();
  }

  await expect(readerItem).toBeVisible({ timeout: 5000 });
  const firstId = (await readerItem.textContent())?.trim().split(" ")[1];
  await readerItem.click();
  if (!isMobileViewport) {
    const csText = (await connectionState.first().textContent()) || "";
    if (csText.includes(reader_id)) {
      return reader_id;
    }
  }
  return firstId as string;
}

export async function postScan(page: Page, message: { reader_id: string; tag_id: string }): Promise<APIResponse> {
  const backendBase = process.env.BACKEND_URL || 'http://localhost:5005';
  const url = backendBase.replace(/\/$/, '') + '/scan';
  return page.request.post(url, { data: message });
}

export async function ensureAppReady(page: Page): Promise<void> {
  const maxAttempts = 3;
  const timeoutPerAttempt = 5000; // ms
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      // prefer a faster DOMContentLoaded readiness check to avoid long networkidle waits
      await page.goto('/', { waitUntil: 'domcontentloaded', timeout: timeoutPerAttempt });
      // successful navigation
      return;
    } catch (err) {
      if (attempt === maxAttempts) {
        throw new Error('Frontend not reachable at baseURL after multiple attempts: please start the frontend server (e.g. npm run dev or docker-compose)');
      }
      // small backoff
      await page.waitForTimeout(500);
    }
  }
}
