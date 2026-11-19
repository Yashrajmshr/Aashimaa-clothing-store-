import { test, expect } from '@playwright/test';

test('admin portal presents staff sign-in instead of using a bundled account', async ({ page }) => {
  await page.goto('/admin/');
  await expect(page.getByRole('heading', { name: 'Staff Sign In' })).toBeVisible();
  await expect(page.getByLabel('Username or mobile')).toBeVisible();
  await expect(page.getByLabel('Password')).toBeVisible();
});

test('customer order details require a verified session', async ({ request }) => {
  const response = await request.get('/api/v1/public/track?booking_number=ASH-8843');
  expect(response.status()).toBe(401);
});
