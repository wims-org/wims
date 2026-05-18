import { test, expect } from "@playwright/test";
import { connectToReader, deleteItemByCode } from "../helpers/sse_subscription";
const { v4: uuidv4 } = require("uuid");
import { postScan } from "../helpers/sse_subscription";

test.beforeEach(async ({ page }) => {
  await page.goto("/");
  await page.context().clearCookies();
  await page.goto("/");
});

test.describe("Item View", () => {
  test("should display empty item form when unknown item is selected", async ({
    page,
  }) => {
    const itemId = uuidv4();
    const message = {
      reader_id: "04-04-46-42-CD-66-84",
      code_value: itemId,
      code_format: "uuid"
    };

    await connectToReader(page, "04-04-46-42-CD-66-84").then(async (readerId) => {
      const resp = await postScan(page, message);
      // this item should not exist
      expect(!resp.ok()).toBeTruthy();
    });
    await page.getByTestId("item-view").waitFor({ timeout: 1500 });
    await expect(page.getByTestId("item-view")).toBeVisible();
    await page.waitForTimeout(500);
    await page.getByTestId("toggle-details-button").click();

    // Check all form fields are empty except for the code field
    const formFields = await page.locator("[data-testid^='form-field-']").all();
    for (const field of formFields) {
      const testId = await field.getAttribute("data-testid");
      const isCodeField = testId === "form-field-code";

      const inputs = await field.locator("input:not([type='checkbox']):not([type='radio'])").all();
      for (const input of inputs) {
        if (await input.isVisible()) {
          await expect(input).toHaveValue(isCodeField ? message.code_value : "");
        }
      }

      const textareas = await field.locator("textarea").all();
      for (const textarea of textareas) {
        if (await textarea.isVisible()) {
          await expect(textarea).toHaveValue("");
        }
      }

      const checkboxes = await field.locator("input[type='checkbox']").all();
      for (const checkbox of checkboxes) {
        if (await checkbox.isVisible()) {
          await expect(checkbox).not.toBeChecked();
        }
      }
    }
  });
  test("should display item form with known item", async ({ page }) => {
    // try to delete item if it exists already to ensure test consistency
    // search item with code
    // delete results if they exist
    const code = "123e4567-e89b-12d3-a456-426614174000";
    await deleteItemByCode(page, code).catch((err) => {
      console.error("Error deleting item by code before test:", err);
    });

    const message = {
      reader_id: "04-04-46-42-CD-66-85",
      code_value: code,
      code_format: "uuid"
    };
    // create item

    await connectToReader(page, "04-04-46-42-CD-66-85").then(async (readerId) => {
      const resp = await postScan(page, message);
      // this item should exist
      expect(resp.ok()).toBeFalsy();
    });
    // fill short name
    await page.getByTestId("item-view").waitFor({ timeout: 1500 });
    await expect(page.getByTestId("item-view")).toBeVisible();
    await page.waitForTimeout(500);
    await page.getByTestId("toggle-details-button").click();

    const shortNameField = await page
      .getByTestId("text-field")
      .filter({ hasText: "Short Name" })
      .first();
    await shortNameField.scrollIntoViewIfNeeded();
    await expect(shortNameField).toBeVisible();
    await shortNameField.locator("input").fill("Hammer");
    // save item
    await page.locator("button[type='submit']", { hasText: "Submit" }).click();
    // wait for save to complete
    await page.waitForTimeout(500);

    // check if item is known

    const resp = await postScan(page, message);
    // this item should exist
    expect(resp.ok()).toBeTruthy();
    // Wait for the connection to be established and for the app to navigate to item view
    await page.waitForTimeout(1000);
    await page.getByTestId("item-view").waitFor({ timeout: 15000 });
    await expect(page.getByTestId("item-view")).toBeVisible();
    await page.getByRole('tab', { name: 'Item Data' }).click();
    // click show details button
    await page.getByTestId("toggle-details-button").click();

    const shortNameInput = await shortNameField.locator("input");
    await shortNameField.scrollIntoViewIfNeeded();
    await expect(shortNameInput).toBeVisible();
    await expect(shortNameInput).toHaveValue("Hammer");
    // delete item
    await page.getByRole("button", { name: "Delete Item" }).click();
  });
});
