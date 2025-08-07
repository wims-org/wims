import { test, expect } from "@playwright/test";
import mqtt from "mqtt";
import { connectToReader } from "../helpers/sse_subscription";
const { v4: uuidv4 } = require("uuid");

const mqttBrokerURL = process.env.MQTT_BROKER_URL || "mqtt://localhost:1883"; // Replace with your broker URL
const mqttTopic = "rfid/scan/reader-1"; // Replace with the topic your backend listens to

let client: mqtt.MqttClient;

test.beforeAll(async () => {
  // Initialize the MQTT client
  client = mqtt.connect(mqttBrokerURL);

  // Wait for the client to connect
  await new Promise((resolve, reject) => {
    client.on("connect", () => {
      console.log("Connected to MQTT broker");
      resolve(true);
    });
    client.on("error", (err) => {
      console.error("Failed to connect to MQTT broker:", err);
      reject(err);
    });
  });
});

test.afterAll(() => {
  // Disconnect the MQTT client
  if (client) {
    client.end();
    console.log("Disconnected from MQTT broker");
  }
});

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
      tag_id: uuidv4(),
    };
    await connectToReader(page, "04-04-46-42-CD-66-84").then(async (readerId) => {
      client.publish(mqttTopic, JSON.stringify(message), { qos: 1 }, (err) => {
        if (err) {
          console.error("Failed to publish message:", err);
        } else {
          console.log("Message published:", message);
        }
      });
    });
    // Wait for the connection to be established
    await page.waitForTimeout(1000);
    // Expect redirection to item view
    await page.waitForURL(/\/items\/[0-9a-fA-F-]*/, { timeout: 5000 });
    await expect(page).toHaveURL(/\/items\/[0-9a-fA-F-]*/);
    await expect(page.getByTestId("item-view")).toBeVisible();
    await page.waitForTimeout(500);
    await expect(page.getByTestId("object-identification")).toContainClass("active");
    await page.getByRole('tab', { name: 'Item Data' }).click();
    // click show details button
    await page.getByTestId("toggle-details-button").click();

    // Check TextField
    const textFields = await page.getByTestId("text-field").all();
    for (const textField of textFields) {
      await textField.scrollIntoViewIfNeeded();
      const input = await textField.locator("input");
      await expect(input).toBeVisible();
      await expect(input).toHaveValue(new RegExp(`^(${message.tag_id}|)$`));
    }

    // Check TextAreaField
    const textAreaFields = await page.getByTestId("text-area-field").all();
    for (const textAreaField of textAreaFields) {
      await textAreaField.scrollIntoViewIfNeeded();
      const textarea = await textAreaField.locator("textarea");
      await expect(textarea).toBeVisible();
      await expect(textarea).toHaveValue("");
    }

    // Check NumberField
    const numberFields = await page.getByTestId("number-field").all();
    for (const numberField of numberFields) {
      await numberField.scrollIntoViewIfNeeded();
      const input = await numberField.locator("input[type='number']");
      await expect(input).toBeVisible();
      await expect(input).toHaveValue("");
    }

    // Check CheckboxField
    const checkboxFields = await page.getByTestId("checkbox-field").all();
    for (const checkboxField of checkboxFields) {
      await checkboxField.scrollIntoViewIfNeeded();
      const checkbox = await checkboxField.locator("input[type='checkbox']");
      await expect(checkbox).toBeVisible();
      await expect(checkbox).not.toBeChecked();
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
      await expect(input).toBeVisible();
      await expect(input).toHaveValue("");
    }
  });
  test("should display item form with known item", async ({ page }) => {
    const message = {
      reader_id: "04-04-46-42-CD-66-85",
      tag_id: "123e4567-e89b-12d3-a456-426614174000",
    };
    await connectToReader(page, "04-04-46-42-CD-66-85").then(async (readerId) => {
      client.publish(mqttTopic, JSON.stringify(message), { qos: 1 }, (err) => {
        if (err) {
          console.error("Failed to publish message:", err);
        } else {
          console.log("Message published:", message);
        }
      });
    });
    // Wait for the connection to be established
    await page.waitForTimeout(1000);
    // Expect redirection to item view
    await page.waitForURL(/\/items\/[0-9a-fA-F-]*/, { timeout: 5000 });
    // Expect redirection to item view
    await expect(page).toHaveURL(/\/items\/[0-9a-fA-F-]*/);
    await page.getByRole('tab', { name: 'Item Data' }).click();
    // click show details button
    await page.getByTestId("toggle-details-button").click();

    // Check TextField with label "short name"
    const shortNameField = await page
      .getByTestId("text-field")
      .filter({ hasText: "Short Name" })
      .first();
    const shortNameInput = await shortNameField.locator("input");
    await shortNameField.scrollIntoViewIfNeeded();
    await expect(shortNameInput).toBeVisible();
    await expect(shortNameInput).toHaveValue("Hammer");
  });
});
