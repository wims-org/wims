import { test, expect } from "@playwright/test";

test.describe("Root View", () => {
  test("should load the root page and display the correct title", async ({ page }) => {
    // Navigate to the root page
    await page.goto("/");

    // Check the page title
    await expect(page).toHaveTitle(/Inventory/); // Replace "Inventory" with your app's title

    // Check for the presence of a key element, e.g., a header
    const header = page.locator("h1");
    await expect(header).toBeVisible();
    await expect(header).toHaveText(/Welcome to Inventory/); // Replace with your actual header text

    // Check for the presence of a navigation bar
    const navBar = page.locator("nav");
    await expect(navBar).toBeVisible();

    // Check for a specific button or link
    const addButton = page.locator("button:has-text('Add Item')");
    await expect(addButton).toBeVisible();
  });

  test("should display an error message if the page fails to load", async ({ page }) => {
    // Simulate a failed page load (e.g., by navigating to a non-existent route)
    await page.goto("/non-existent-route");

    // Check for an error message
    const errorMessage = page.locator(".alert-danger");
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toHaveText(/Error loading item details/); // Replace with your actual error message
  });
});