/**
 * Demo mode for screen recordings: makes every Playwright interaction easy to follow on video.
 *
 *   import { installDemoMode } from './demoMode';
 *   test('...', async ({ page }) => { installDemoMode(page); ... });
 *
 * Patches Locator.prototype once per worker, so it covers every click in the spec AND in the
 * shared QA helpers it calls (createClient, questionnaire, ...) without editing them, and every
 * page/popup/context created afterwards (Locator is one class for the whole process).
 *
 * For click-like actions (click, dblclick, tap, check, uncheck, setChecked, selectOption):
 *   1. wait for the target to be visible (respecting the caller's own `timeout`, so try/catch
 *      probes with short timeouts keep their meaning),
 *   2. if it isn't fully inside the viewport, smooth-scroll it to the centre of the screen,
 *   3. glide a visible cursor to it and draw a pulsing highlight ring around it,
 *   4. ripple at the click point and perform the real action,
 *   5. hold for DEMO_CLICK_PAUSE_MS (default 3000) so the viewer sees what the click did.
 * Typing actions (fill, pressSequentially, type) get steps 1-3 and a shorter hold.
 *
 * The overlay is drawn in the top-level page with pointer-events:none, so it never intercepts
 * input, and it also works for elements inside iframes (Stripe's card fields). Set
 * DEMO_MODE=0 to turn it off for a quick functional run.
 */
import type { Locator, Page } from '@playwright/test';

const CLICK_PAUSE_MS = Number(process.env.DEMO_CLICK_PAUSE_MS ?? 3000);
const TYPE_PAUSE_MS = Number(process.env.DEMO_TYPE_PAUSE_MS ?? 1000);
const SCROLL_SETTLE_MS = 900;
const GLIDE_MS = 550;
const DWELL_MS = 450;

type Box = { x: number; y: number; width: number; height: number };
const lastCursor = new WeakMap<Page, { x: number; y: number }>();
let installed = false;

/** Draws/updates the overlay in the page's top frame. Self-contained so it survives navigations. */
async function overlay(page: Page, action: 'target' | 'ripple' | 'clear', box?: Box, from?: { x: number; y: number }) {
    await page.evaluate(({ action, box, from, glideMs }) => {
        const Z = '2147483647';
        const doc = document;
        if (!doc.body) return;
        if (!doc.getElementById('__demoStyle')) {
            const st = doc.createElement('style');
            st.id = '__demoStyle';
            st.textContent = `
              @keyframes __demoPulse { 0%,100% { box-shadow: 0 0 0 0 rgba(245,158,11,.55), 0 0 18px rgba(245,158,11,.45); }
                                       50% { box-shadow: 0 0 0 8px rgba(245,158,11,0), 0 0 26px rgba(245,158,11,.65); } }
              @keyframes __demoRipple { from { transform: translate(-50%,-50%) scale(.2); opacity: .75; }
                                        to { transform: translate(-50%,-50%) scale(2.6); opacity: 0; } }
              #__demoCursor { position: fixed; left: 0; top: 0; width: 26px; height: 26px; z-index: ${Z};
                              pointer-events: none; transition: left ${glideMs}ms cubic-bezier(.4,0,.2,1), top ${glideMs}ms cubic-bezier(.4,0,.2,1);
                              filter: drop-shadow(0 2px 3px rgba(0,0,0,.35)); }
              #__demoRing { position: fixed; z-index: ${Z}; pointer-events: none; border: 3px solid #f59e0b;
                            border-radius: 8px; animation: __demoPulse 1s ease-in-out infinite; transition: opacity .35s; }
              .__demoRipple { position: fixed; z-index: ${Z}; pointer-events: none; width: 46px; height: 46px;
                              border-radius: 50%; background: rgba(245,158,11,.55); border: 2px solid #f59e0b;
                              animation: __demoRipple .65s ease-out forwards; }`;
            (doc.head || doc.documentElement).appendChild(st);
        }
        let cursor = doc.getElementById('__demoCursor');
        if (!cursor) {
            cursor = doc.createElement('div');
            cursor.id = '__demoCursor';
            cursor.innerHTML = '<svg viewBox="0 0 24 24" width="26" height="26"><path d="M4 2 L4 20 L9 15.5 L12.5 22 L15.5 20.5 L12 14 L19 14 Z" fill="#111" stroke="#fff" stroke-width="1.6" stroke-linejoin="round"/></svg>';
            if (from) { cursor.style.transition = 'none'; cursor.style.left = `${from.x}px`; cursor.style.top = `${from.y}px`; }
            doc.body.appendChild(cursor);
            void cursor.offsetWidth; // commit the start position before the glide transition
            cursor.style.transition = '';
        }
        const ring = doc.getElementById('__demoRing');
        if (action === 'clear') {
            if (ring) { ring.style.opacity = '0'; setTimeout(() => ring.remove(), 400); }
            return;
        }
        if (!box) return;
        const cx = box.x + box.width / 2, cy = box.y + box.height / 2;
        if (action === 'target') {
            cursor.style.left = `${cx - 4}px`;
            cursor.style.top = `${cy - 2}px`;
            const r = ring || doc.createElement('div');
            r.id = '__demoRing';
            const pad = 5;
            Object.assign(r.style, {
                left: `${box.x - pad}px`, top: `${box.y - pad}px`,
                width: `${box.width + pad * 2}px`, height: `${box.height + pad * 2}px`, opacity: '1',
            });
            if (!ring) doc.body.appendChild(r);
        } else {
            const rp = doc.createElement('div');
            rp.className = '__demoRipple';
            rp.style.left = `${cx}px`;
            rp.style.top = `${cy}px`;
            doc.body.appendChild(rp);
            setTimeout(() => rp.remove(), 800);
        }
    }, { action, box, from, glideMs: GLIDE_MS }).catch(() => { /* page mid-navigation: skip the effect */ });
}

/** Visible box to point at: the element itself, or its <label> when the input is visually hidden. */
async function targetBox(loc: Locator): Promise<Box | null> {
    let box = await loc.boundingBox().catch(() => null);
    if (box && (box.width < 6 || box.height < 6)) {
        const label = loc.locator('xpath=ancestor::label[1]');
        if (await label.count().catch(() => 0)) box = (await label.first().boundingBox().catch(() => null)) ?? box;
    }
    return box;
}

/** Steps 1-3 above. Returns the box it pointed at, or null if the effect was skipped. */
async function present(loc: Locator, timeout: number | undefined): Promise<Box | null> {
    const page = loc.page();
    try {
        await loc.waitFor({ state: 'visible', ...(timeout !== undefined ? { timeout } : {}) });
    } catch {
        return null; // let the real action decide what happens (and fail with its own error)
    }
    let box = await targetBox(loc);
    const vp = page.viewportSize();
    const inView = (b: Box | null) => !!b && !!vp &&
        b.y >= 0 && b.x >= 0 && b.y + b.height <= vp.height && b.x + b.width <= vp.width;
    if (!inView(box)) {
        await loc.evaluate((el: Element) => el.scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'nearest' })).catch(() => {});
        await page.waitForTimeout(SCROLL_SETTLE_MS);
        await loc.scrollIntoViewIfNeeded({ timeout: 5000 }).catch(() => {}); // e.g. iframe content: scroll the outer page too
        box = await targetBox(loc);
    }
    if (!box) return null;
    const from = lastCursor.get(page) ?? (vp ? { x: vp.width / 2, y: vp.height / 2 } : { x: 0, y: 0 });
    await overlay(page, 'target', box, from);
    lastCursor.set(page, { x: box.x + box.width / 2, y: box.y + box.height / 2 });
    await page.waitForTimeout(GLIDE_MS + DWELL_MS);
    return box;
}

export function installDemoMode(page: Page) {
    if (installed || process.env.DEMO_MODE === '0') return;
    installed = true;
    const proto = Object.getPrototypeOf(page.locator('body')) as Record<string, any>;

    const clickLike = ['click', 'dblclick', 'tap', 'check', 'uncheck', 'setChecked', 'selectOption'];
    for (const name of clickLike) {
        const original = proto[name];
        if (typeof original !== 'function') continue;
        proto[name] = async function (this: Locator, ...args: any[]) {
            // setChecked(checked, options) / selectOption(values, options) put options second.
            const opts = (name === 'setChecked' || name === 'selectOption') ? args[1] : args[0];
            if (opts?.trial) return original.apply(this, args);
            const page = this.page();
            const box = await present(this, opts?.timeout);
            if (box) await overlay(page, 'ripple', box);
            const result = await original.apply(this, args);
            await page.waitForTimeout(CLICK_PAUSE_MS).catch(() => {});
            if (box) await overlay(page, 'clear');
            return result;
        };
    }

    for (const name of ['fill', 'pressSequentially', 'type']) {
        const original = proto[name];
        if (typeof original !== 'function') continue;
        proto[name] = async function (this: Locator, ...args: any[]) {
            const page = this.page();
            const box = await present(this, args[1]?.timeout);
            const result = await original.apply(this, args);
            await page.waitForTimeout(TYPE_PAUSE_MS).catch(() => {});
            if (box) await overlay(page, 'clear');
            return result;
        };
    }
    console.log(`[demoMode] on: scroll-to-target, cursor + highlight + ripple, ${CLICK_PAUSE_MS}ms after each click`);
}
