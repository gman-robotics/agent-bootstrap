/** Quick local check of demoMode: off-screen target scrolls in, overlay renders, 3s hold applies. */
import { test, expect } from '@playwright/test';
import { installDemoMode } from './demoMode';

test.use({ viewport: { width: 1280, height: 800 }, video: { mode: 'on', size: { width: 1280, height: 800 } } });

test('demo mode smoke', async ({ page }, testInfo) => {
    installDemoMode(page);
    await page.setContent(`<body style="font-family:sans-serif">
      <button id="a" onclick="this.textContent='A clicked'">Top button</button>
      <div style="height:2200px"></div>
      <label style="display:inline-block;padding:8px;border:1px solid #ccc"><input type="radio" name="r" id="r" style="position:absolute;width:1px;height:1px;opacity:0">Hidden-input radio</label>
      <input id="t" placeholder="type here"><button id="b" onclick="this.textContent='B clicked'">Far button</button></body>`);
    const t0 = Date.now();
    await page.locator('#a').click();
    const t1 = Date.now();
    await page.locator('#b').scrollIntoViewIfNeeded().catch(() => {}); // no-op path check not needed
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.getByRole('radio', { name: 'Hidden-input radio' }).check();
    await page.locator('#t').fill('hello');
    // Capture mid-highlight: start the click and screenshot before it finishes.
    const p = page.locator('#b').click();
    await page.waitForTimeout(1200);
    await page.screenshot({ path: testInfo.outputPath('mid-click.png') });
    await p;
    const scrollY = await page.evaluate(() => window.scrollY);
    console.log(JSON.stringify({ firstClickMs: t1 - t0, scrollY, b: await page.locator('#b').innerText(), checked: await page.locator('#r').isChecked() }));
    expect(t1 - t0).toBeGreaterThanOrEqual(3000);
    expect(scrollY).toBeGreaterThan(1000);
    await expect(page.locator('#b')).toHaveText('B clicked');
    expect(await page.locator('#r').isChecked()).toBe(true);
});
