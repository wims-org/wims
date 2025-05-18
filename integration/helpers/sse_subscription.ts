import { expect } from "playwright/test";

export async function connectToReader(page, reader_id: string): Promise<void> {
  await page.goto("/readers");
  await page.getByTestId("reader-list").waitFor();
  const connectionState = page.getByTestId("sse-connection-state");
  await expect(connectionState).toBeVisible();
  await expect(connectionState).toHaveText(
    /🔴 Not Connected to a reader, choose one a/
  );

  const firstItem = page.getByTestId("reader-item").first();
  const firstId = await firstItem.textContent().then((text) => {
    return text?.trim().split(" ")[1];
  });
  await firstItem.click();
  await expect(connectionState).toHaveText("Connecting to backend...");
  await expect(connectionState).toHaveText(
    "🟢 Connected to Reader with id " + firstId
  );
}
