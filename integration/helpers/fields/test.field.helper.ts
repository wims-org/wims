import { Locator } from "playwright/test";

export async function getFieldValue(page, field: Locator): Promise<string> {
  const fieldValue = await field.evaluate((el) => {
    return (el as HTMLInputElement).value;
  });
  return fieldValue;
}
