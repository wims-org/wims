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
    const message = {
      reader_id: "04-04-46-42-CD-66-84",
      code_value: uuidv4(),
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
    await expect(page.getByTestId("object-identification")).toContainClass("active");
    await page.getByRole('tab', { name: 'Item Data' }).click();
    await page.getByTestId("toggle-details-button").click();

    // Check TextField
    const textFields = await page.getByTestId("text-field").all();
    for (const textField of textFields) {
      const input = await textField.locator("input");
      if (await input.isVisible()) {
        await expect(input).toHaveValue(new RegExp(`^(${message.code_value}|)$`));
      }
    }

    // Check TextAreaField
    const textAreaFields = await page.getByTestId("text-area-field").all();
    for (const textAreaField of textAreaFields) {
      const textarea = await textAreaField.locator("textarea");
      if (await textarea.isVisible()) {
        await expect(textarea).toHaveValue("");
      }
    }

    // Check NumberField
    const numberFields = await page.getByTestId("number-field").all();
    for (const numberField of numberFields) {
      const input = await numberField.locator("input[type='number']");
      if (await input.isVisible()) {
        await expect(input).toHaveValue("");
      }
    }

    // Check CheckboxField
    const checkboxFields = await page.getByTestId("checkbox-field").all();
    for (const checkboxField of checkboxFields) {
      const checkbox = await checkboxField.locator("input[type='checkbox']");
      if (await checkbox.isVisible()) {
        await expect(checkbox).not.toBeChecked();
      }
    }

    // Check ArrayField
    const arrayFields = await page.getByTestId("array-field").all();
    for (const arrayField of arrayFields) {
      const pills = await arrayField.locator(".pill").all();
      expect(pills.length).toBe(0);
    }

    // Check ObjectField
    const objectFields = await page.getByTestId("object-field").all();
    for (const objectField of objectFields) {
      const inputs = await objectField.locator("input").all();
      for (const input of inputs) {
        await expect(input).toBeVisible();
        await expect(input).toHaveValue("");
      }
    }

    // Check ImageThumbnailField
    const imageThumbnailFields = await page
      .getByTestId("image-thumbnail-field")
      .all();
    for (const imageThumbnailField of imageThumbnailFields) {
      const thumbnails = await imageThumbnailField.locator(".thumbnail").all();
      expect(thumbnails.length).toBe(0);
    }

    // Check LoadingField
    const loadingFields = await page.getByTestId("loading-field").all();
    for (const loadingField of loadingFields) {
      await expect(loadingField).toBeVisible();
    }

    // Check ModalField
    const modalFields = await page.getByTestId("modal-field").all(); // ModalField uses the same data-testid as TextAreaField
    for (const modalField of modalFields) {
      const input = await modalField.locator("input");
      if (await input.isVisible()) {
        await expect(input).toHaveValue("");
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
    await expect(page.getByTestId("object-identification")).toContainClass("active");
    await page.getByRole('tab', { name: 'Item Data' }).click();
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
