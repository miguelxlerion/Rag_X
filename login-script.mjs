export default async function(page, ui) {
  await page.waitForTimeout(1000);
  const userInput = page.locator('input[name="username"]');
  const passInput = page.locator('input[name="password"]');
  if (await userInput.isVisible()) {
    await userInput.fill('admin');
    await passInput.fill('admin123');
    await page.locator('input[type="submit"]').click();
    await page.waitForTimeout(2000);
    return { loggedIn: true };
  }
  return { alreadyLoggedIn: true };
}