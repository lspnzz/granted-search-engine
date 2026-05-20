import { expect, test } from '@playwright/test';

test('search page returns mock grants', async ({ page }) => {
  await page.goto('/');
  await page.getByPlaceholder("Describe what you're working on, in depth").fill('AI medical imaging');
  await page.keyboard.press('Enter');

  await expect(page.getByText('Deployment of cutting-edge multi-modal AI-based solutions in medical imaging')).toBeVisible();
});

test('agent page can reach mock search results', async ({ page }) => {
  await page.goto('/agent');
  await expect(page.getByText('Pitch Assistant')).toBeVisible();
  await expect(page.getByText(/What problem does your project solve/)).toBeVisible();

  await page.getByPlaceholder('Type your response...').fill('We build AI medical imaging tools for hospitals to improve diagnostic workflows.');
  await page.getByRole('button', { name: 'Send message' }).click();

  await expect(page.getByText(/mock search pitch for review/)).toBeVisible();

  await page.getByPlaceholder('Type your response...').fill('yes');
  await page.getByRole('button', { name: 'Send message' }).click();

  await expect(page.getByRole('heading', { name: 'Matching EU Grants' })).toBeVisible();
});
