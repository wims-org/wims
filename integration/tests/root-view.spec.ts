import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("http://localhost:8080/");
  await page.context().clearCookies();
});

test.describe("Root View", () => {
  test("should display an error message if the page fails to load", async ({
    page,
  }) => {
    // Simulate a failed page load (e.g., by navigating to a non-existent route)
    await page.goto("/non-existent-route");

    // Check for an error message
    const errorMessage = page.locator(".alert-danger");
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toHaveText(/Error loading item details/); // Replace with your actual error message
  });

  test("should display navigation list", async ({ page }) => {
    await page.goto("http://localhost:8080/");
    await expect(page).toHaveTitle(/WIMS/);
    await expect(
      page.getByRole("listitem").filter({ hasText: "Items" })
    ).toBeVisible();
    await expect(
      page.getByRole("listitem").filter({ hasText: "Readers" })
    ).toBeVisible();
  });

  test("should subscribe to reader stream", async ({ page }) => {
    await page.goto("http://localhost:8080/readers");
    await page.getByTestId("reader-list").waitFor();
    // sse-connection-state
    const connectionState = page.getByTestId("sse-connection-state");
    await expect(connectionState).toBeVisible();
    // .toHaveText("Connected");
    await expect(connectionState).toHaveText(
      /🔴 Not Connected to a reader, choose one a/
    );

    const firstItem = page.getByTestId("reader-item").first();
    const firstId = await firstItem.textContent().then((text) => {
      return text?.trim().split(" ")[1];
    });
    await firstItem.click();
    // " Connecting to backend... "
    await expect(connectionState).toHaveText("Connecting to backend...");
    // Wait until for the connection state to change with polling
    await expect(connectionState).toHaveText(
      "🟢 Connected to Reader with id " + firstId
    );
  });
  
  test("should be able to add readers", async ({ page }) => {
    await page.goto("http://localhost:8080/readers");
    await page.getByTestId("reader-list").waitFor();

    const initialListLength = await page.getByTestId("reader-item").count();

    // Fill in the reader details
    await page.getByRole("textbox", { name: "Reader Name" }).fill("Reader-5");
    await page
      .getByRole("textbox", { name: "Reader ID" })
      .fill("04-04-46-42-CD-66-83");
    await page.getByRole("button", { name: "Add Reader" }).click();

    // Wait for the new reader to appear in the list
    const newReader = page.getByTestId("reader-item").last();
    await expect(newReader).toBeVisible();
    expect(newReader).toHaveText(/Reader-5 04-04-46-42-CD-66-83/);

    // Verify the list length has increased by 1
    const updatedListLength = await page.getByTestId("reader-item").count();
    expect(updatedListLength).toBe(initialListLength + 1);
  });
});
