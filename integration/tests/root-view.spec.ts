import { test, expect } from "@playwright/test";
import { connectToReader } from "../helpers/sse_subscription";


test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.context().clearCookies();
});

test.describe.configure({ mode: "serial" });

test.describe("Root View", () => {
  // Too: Skip this test, there is no error page yet
  test.skip("should display an error message if the page fails to load", async ({
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
    await page.goto("/");
    await expect(page).toHaveTitle(/WIMS/);
    await expect(
      page.getByRole("listitem").filter({ hasText: "Items" })
    ).toBeVisible();
    await expect(
      page.getByRole("listitem").filter({ hasText: "Readers" })
    ).toBeVisible();
  });

  test("should subscribe to reader stream", async ({ page }) => {
    await connectToReader(page, "04-04-46-42-CD-66-81");
  });
  
  test("should be able to add and delete readers", async ({ page }) => {
    await page.goto("/readers");
    await page.getByTestId("reader-list").waitFor();

    const initialListLength = await page.getByTestId("reader-item").count();
    // Fill in the reader details
    await page.getByRole("textbox", { name: "Reader Name" }).fill("Reader-5");
    await page
      .getByRole("textbox", { name: "Reader ID" })
      .fill("04-04-46-42-CD-66-83");
    await page.getByRole("button", { name: "Add Reader" }).click();
    await page.waitForTimeout(100); // Wait for the reader to be added
    // Wait for the new reader to appear in the list
    const newReader = page.getByTestId("reader-item").last();
    await expect(newReader).toBeVisible();
    expect(newReader).toHaveText(/Reader-5 04-04-46-42-CD-66-83/);

    // Verify the list length has increased by 1
    var updatedListLength = await page.getByTestId("reader-item").count();
    expect(updatedListLength).toBe(initialListLength + 1);
 
    // Verify the list length has decreased by 1
    await newReader.getByRole("button", { name: "Delete" }).click()
    await page.waitForTimeout(100); // Wait for the reader to be deleted
    updatedListLength = await page.getByTestId("reader-item").count();
    expect(updatedListLength).toBe(initialListLength);
  });
});
