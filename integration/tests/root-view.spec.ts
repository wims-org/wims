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
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto("/");
    await expect(page).toHaveTitle(/WIMS/);
    const navList = page.getByTestId('home-nav-list');
    await navList.waitFor({ timeout: 5000 });
    await expect(navList).toBeVisible();
    await expect(navList.getByText('Items', { exact: true })).toBeVisible();
    await expect(navList.getByText('Readers', { exact: true })).toBeVisible();
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

    // Verify the new reader exists in the list
    await expect(page.getByText("Reader-5 04-04-46-42-CD-66-83")).toBeVisible();

    // Delete the new reader and verify it is removed
    await newReader.getByRole("button", { name: "Delete" }).click();
    await page.waitForTimeout(100); // Wait for the reader to be deleted
    await expect(page.getByText("Reader-5 04-04-46-42-CD-66-83")).toHaveCount(0);
  });
});
