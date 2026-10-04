/**
 * One-time: accept the "Updates to our Terms of Service and Privacy Agreement" dialog that a new
 * partner-portal user gets on first sign-in (userData.forceWelcome = TERMS_AND_CONDITIONS), then
 * refresh the saved storageState. Clicks the real checkboxes/button so the app records acceptance
 * through its own path.
 *
 *   LOGIN_HOST=familybankstaging.estateguru.com LOGIN_OUT=tests/scratch/.auth-fbs.json \
 *   npx playwright test tests/scratch/accept-agreements.setup.spec.ts --project=chromium --reporter=line
 */
import { test, expect } from '@playwright/test';
import * as path from 'path';

const OUT = path.resolve(process.env.LOGIN_OUT ?? 'tests/scratch/.auth-fbs.json');
test.use({ storageState: OUT });

test('accept agreement updates', async ({ page, context }) => {
    test.setTimeout(2 * 60 * 1000);
    await page.goto(`https://${process.env.LOGIN_HOST}/app/partner`, { waitUntil: 'domcontentloaded' });
    const dialog = page.locator('#agreementUpdateSection');
    const shown = await dialog.waitFor({ state: 'visible', timeout: 20_000 }).then(() => true).catch(() => false);
    if (shown) {
        await page.locator('#agreement_termsAndPrivacy').check();
        const partnership = page.locator('#agreement_partnership');
        if (await partnership.isVisible().catch(() => false)) await partnership.check();
        const [resp] = await Promise.all([
            page.waitForResponse(r => r.request().method() !== 'GET' && /\/api\//.test(r.url()), { timeout: 30_000 }),
            page.getByRole('button', { name: 'I agree to the updates' }).click(),
        ]);
        console.log(`[agreements] ${resp.request().method()} ${new URL(resp.url()).pathname} -> ${resp.status()}`);
        await expect(dialog).toBeHidden({ timeout: 30_000 });
    } else {
        console.log('[agreements] no agreement dialog shown');
    }
    await page.reload({ waitUntil: 'domcontentloaded' });
    await expect(page.getByRole('button', { name: 'Add a client' })).toBeEnabled({ timeout: 30_000 });
    await expect(dialog).toBeHidden();
    await context.storageState({ path: OUT });
    console.log('[agreements] partner portal usable; session saved');
});
