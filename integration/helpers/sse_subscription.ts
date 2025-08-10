import { expect } from "playwright/test";

export async function connectToReader(page, reader_id: string): Promise<string> {
  await page.goto("/readers");
  await page.getByTestId("reader-list").waitFor();
  const connectionState = page.getByTestId("sse-connection-state");
  await expect(connectionState).toBeVisible();
  if (await connectionState.textContent().then((text) => text?.includes("Connecting to backend..."))) {
    // already connecting, wait for it to finish
    await expect(connectionState).toContainText("Connected to Reader with id");
  }
  if (await connectionState.textContent().then((text) => text?.includes("Connected to Reader with id " + reader_id))) {
    return reader_id; // already connected
  } else {
    await expect(connectionState).toHaveText(
      /🔴 Not Connected to a reader, choose one a/
    );
  }
  let readerItem = page.getByTestId("reader-item").filter({ hasText: reader_id }).first();
  // create a reader item with the given reader_id
  if (await readerItem.count() === 0) {
    // if no reader item is found, create one
    await page.getByRole("textbox", { name: "Reader Name" }).fill("Reader-" + reader_id);
    await page
      .getByRole("textbox", { name: "Reader ID" })
      .fill(reader_id);
    await page.getByRole("button", { name: "Add Reader" }).click();
    await page.waitForTimeout(100); // Wait for the reader to be added

    readerItem = page.getByTestId("reader-item").filter({ hasText: reader_id }).first();
  }
  await expect(readerItem).toBeVisible();
  const firstId = await readerItem.textContent().then((text) => {
    return text?.trim().split(" ")[1];
  });
  await readerItem.click();
  //  await expect(connectionState).toHaveText("Connecting to backend...");
  await page.waitForTimeout(1000); // wait for connection to be established
  await expect(connectionState).toHaveText(
    "🟢 Connected to Reader with id " + firstId
  );
  return firstId as string;
}
