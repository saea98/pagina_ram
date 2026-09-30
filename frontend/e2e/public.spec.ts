import AxeBuilder from '@axe-core/playwright'
import { expect, test } from '@playwright/test'

const pages = [
  '/',
  '/servicios/mezcla',
  '/portafolio',
  '/portafolio/palenque',
  '/equipo/alejandro-vega',
  '/aviso-de-privacidad',
  '/links',
]

for (const path of pages) {
  test(`${path} has no serious axe violations`, async ({ page }) => {
    await page.goto(path)
    await expect(page.locator('h1, h2').first()).toBeVisible()
    const results = await new AxeBuilder({ page }).withTags(['wcag2a', 'wcag2aa']).analyze()
    const serious = results.violations.filter((violation) =>
      ['serious', 'critical'].includes(violation.impact || ''),
    )
    expect(serious, JSON.stringify(serious, null, 2)).toEqual([])
  })
}

async function openReady(page: import('@playwright/test').Page, path: string) {
  await page.goto(path)
  await page.locator('html[data-hydrated="true"]').waitFor()
}

test('service card flips from the keyboard', async ({ page }) => {
  await openReady(page, '/')
  const card = page.getByRole('button', { name: 'Composición' })
  await card.focus()
  await card.press('Enter')
  await expect(card).toHaveAttribute('aria-pressed', 'true')
})

test('contact form creates a lead', async ({ page }) => {
  await openReady(page, '/#contacto')
  await page.locator('#lead-name').fill('Ada Lovelace')
  await page.locator('#lead-email').fill(`ada-${Date.now()}@example.com`)
  await page.locator('#lead-message').fill('Quiero grabar un EP de cinco temas.')
  await page.getByRole('button', { name: 'Enviar mensaje →' }).click()
  await expect(page.locator('#lead-thanks')).toContainText('Recibimos tu mensaje')
})

test('own audio keeps playing after navigation', async ({ page }) => {
  await openReady(page, '/')
  const card = page.locator('#portafolio .embed-card', { hasText: 'Neto' })
  await card.getByRole('button', { name: 'Escuchar' }).click()
  const audio = page.getByTestId('global-audio')
  await expect
    .poll(async () => audio.evaluate((element) => (element as HTMLAudioElement).paused))
    .toBe(false)
  await page.getByRole('link', { name: 'Aviso de privacidad' }).first().click()
  await expect(page).toHaveURL(/\/aviso-de-privacidad$/)
  await expect
    .poll(async () => audio.evaluate((element) => (element as HTMLAudioElement).paused))
    .toBe(false)
})
