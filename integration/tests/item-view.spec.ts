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
  test("should display empty item form when unknown item is selected", async ({
    page,
  }) => {
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
    // expect redirection to item view
    await expect(page).toHaveURL(/\/items\/[0-9a-fA-F-]*/);

    const locator_list = await page.getByRole("textbox").all();
    // for x in locator_list
    locator_list.forEach(async (input) => {
      await expect(input).toBeVisible();
      await expect(input).toHaveValue(new RegExp(`^(${message.tag_id}|)$`));
    });
  });
});
