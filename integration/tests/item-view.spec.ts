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
  await connectToReader(page, "04-04-46-42-CD-66-81");
  await page.goto("/");
});

test.describe("Item View", () => {
  test("should display empty item form when unknown item is selected", async ({ page }) => {
    // Publish a message
    const message = {
      reader_id: "04-04-46-42-CD-66-81",
      tag_id: uuidv4(),
    };
    client.publish(mqttTopic, JSON.stringify(message), { qos: 1 }, (err) => {
      if (err) {
        console.error("Failed to publish message:", err);
      } else {
        console.log("Message published:", message);
      }
    });
    await page.waitForTimeout(3500);

    // Expect redirection to item view
    await expect(page).toHaveURL(/\/items\/[0-9a-fA-F-]*/);
    // click show details button
    await page.getByTestId("toggle-details-button").click();

    // Check TextField
    const textFields = await page.getByTestId("text-field").all();
    for (const textField of textFields) {
      const input = await textField.locator("input");
      await expect(input).toBeVisible();
      await expect(input).toHaveValue(new RegExp(`^(${message.tag_id}|)$`));
      
    }

    // Check TextAreaField
    const textAreaFields = await page.getByTestId("text-area-field").all();
    for (const textAreaField of textAreaFields) {
      const textarea = await textAreaField.locator("textarea");
      await expect(textarea).toBeVisible();
      await expect(textarea).toHaveValue("");
    }

    // Check NumberField
    const numberFields = await page.getByTestId("number-field").all();
    for (const numberField of numberFields) {
      const input = await numberField.locator("input[type='number']");
      await expect(input).toBeVisible();
      await expect(input).toHaveValue("");
    }

    // Check CheckboxField
    const checkboxFields = await page.getByTestId("checkbox-field").all();
    for (const checkboxField of checkboxFields) {
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
    const imageThumbnailFields = await page.getByTestId("image-thumbnail-field").all();
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
    const modalFields = await page.getByTestId("text-area-field").all(); // ModalField uses the same data-testid as TextAreaField
    for (const modalField of modalFields) {
      const textarea = await modalField.locator("textarea");
      await expect(textarea).toBeVisible();
      await expect(textarea).toHaveValue("");
    }
  });
});
