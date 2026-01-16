import { defineConfig, devices } from "@playwright/test";
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '.env') });

const frontendURL = process.env.CI == "true" ? "http://proxy:80" : "http://localhost:5173";

console.log(`Running tests against frontend URL: ${frontendURL}, CI mode: ${process.env.CI}`);

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: "html",
  use: {
    baseURL: frontendURL,
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
  ],
  // webServer: {
  //   command: "./scripts/start.sh",
  //   port: 5173,
  //   reuseExistingServer: !process.env.CI,
  // },
});
