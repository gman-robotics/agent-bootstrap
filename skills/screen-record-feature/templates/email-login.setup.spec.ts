/**
 * Passwordless sign-in for scratch recordings: request an email sign-in link on a white label's
 * own host, read it from testmail.app (the QA suite's TestMailAppProvider), open it, and save the
 * resulting storageState. No password is ever created, typed, or stored.
 *
 *   LOGIN_HOST=familybankstaging.estateguru.com LOGIN_EMAIL=<namespace>.<demo-user>@inbox.testmail.app \
 *   LOGIN_OUT=tests/scratch/.auth-fbs.json \
 *   npx playwright test tests/scratch/email-login.setup.spec.ts --project=chromium --reporter=line
 *
 * The account must be loginCreated=1 + active, and EMAIL_LOGIN_ENABLED must cover its white label
 * (POST /api/user/emaillogin returns the same 200 whether or not it sent anything).
 */
import { test, expect } from '@playwright/test';
import * as path from 'path';
import { TestMailAppProvider } from '../utils/testMailAppProvider';

test('email-link sign-in -> storageState', async ({ page, context }) => {
    test.setTimeout(4 * 60 * 1000);
    const host = process.env.LOGIN_HOST!;
    const email = process.env.LOGIN_EMAIL!;
    const outFile = path.resolve(process.env.LOGIN_OUT!);
    expect(host && email && outFile, 'LOGIN_HOST / LOGIN_EMAIL / LOGIN_OUT required').toBeTruthy();
    const mail = new TestMailAppProvider();

    await page.goto(`https://${host}/app/`, { waitUntil: 'domcontentloaded' });

    // Snapshot the inbox first so a link from an earlier run can never be picked up.
    const before = new Set((await mail.getMessages(email)).map(m => m.id));
    const since = Date.now() - 5_000;

    // Same call the login page's "Continue with an email link" makes (EmailSignIn.tsx); with no
    // whiteLabelId in the body the server scopes it to this host's white label from the session.
    const status = await page.evaluate(async (addr) => {
        const r = await fetch('/api/user/emaillogin', {
            method: 'POST', credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: addr }),
        });
        return r.status;
    }, email);
    console.log(`[emailLogin] POST /api/user/emaillogin -> ${status}`);
    expect(status).toBe(200);

    const msg = await mail.waitForEmail(email, { since, newest: true, excludeIds: before, timeout: 120_000 });
    const body = `${msg.html ?? ''}\n${msg.text ?? ''}\n${msg.body}`;
    const link = body.match(/https:\/\/[^\s"'<>]+\/app\/email-signin\/[A-Za-z0-9-]+/)?.[0];
    expect(link, `no /app/email-signin/ link in "${msg.subject}"`).toBeTruthy();
    console.log(`[emailLogin] got "${msg.subject}" -> ${new URL(link!).host}/app/email-signin/<token>`);

    await page.goto(link!, { waitUntil: 'domcontentloaded' });
    // EmailSignInConfirm consumes the token and redirects into /app once the session exists.
    await page.waitForURL(u => !u.pathname.includes('/email-signin/'), { timeout: 60_000 });
    await page.waitForLoadState('networkidle', { timeout: 15_000 }).catch(() => {});
    const me = await page.evaluate(async () => (await fetch('/api/usercache', { credentials: 'include' })).status);
    console.log(`[emailLogin] landed on ${new URL(page.url()).pathname}; /api/usercache -> ${me}`);
    expect(me).toBe(200);

    await context.storageState({ path: outFile });
    console.log(`[emailLogin] saved session -> ${outFile}`);
});
