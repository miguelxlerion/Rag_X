export default async function(page, ui) {
  // Click on "Modelos Gratis" tab
  const freeTab = page.locator('button:has-text("Modelos Gratis")');
  if (await freeTab.isVisible()) {
    await freeTab.click();
    await page.waitForTimeout(1000);
  }
  return { clicked: true };
}