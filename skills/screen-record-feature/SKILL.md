---
name: screen-record-feature
description: "Record an easy-to-follow screen video of a web app feature with Playwright: scripted end-to-end flow, visible cursor, click highlights and pauses, frozen-tab cuts, and full plus short MP4s."
version: 1.0.0
---

# screen-record-feature — Playwright feature demo videos

**Purpose**
Produce a screen recording of a real feature, running end to end against a test environment.
The viewer should be able to follow every step: the target is scrolled into view, a cursor glides
to it, it is highlighted and the click ripples, then the video holds long enough to see the result.
The output is a full MP4 plus a short cut, both checked by eye before delivery.

**Trigger**
"Record a video of <feature>", "screen-record <flow>", "make a demo video", or "show the team how
<feature> works" on a web app with a Playwright suite.

**Do not use for**
- Functional QA with no video → the repo's normal Playwright suite or `black-box-agent-qa`
- A static walkthrough of the shape of a change → `show-me`
- Exploratory bug hunting → `debug-investigation`

---

## Companions

| Skill | Role here |
|---|---|
| `how` | Read the feature's views and API routes before scripting it |
| `reply-contract` | Final delivery message (timeline table, side effects) |
| `unslop` | Last pass on the delivery message |

---

## Overview

A recording is a Playwright spec run with video on, plus the demo-mode overlay, plus an assembly
step. Write it as a throwaway "scratch" spec next to the suite, reusing the suite's helpers for
setup. It is not part of the suite. The video is only as good as the run, so the work is mostly
getting a clean end-to-end pass, then cutting the per-tab videos into one story.

## Files

| Path | What it is |
|---|---|
| `scripts/demoMode.ts` | The overlay. `installDemoMode(page)` at the top of the test. |
| `scripts/demoMode.smoke.spec.ts` | 15-second local check of the overlay (no app needed). |
| `scripts/assemble-segments.sh` | Joins explicit `file.webm[:start[:end]]` ranges in story order, writes `<out>-contact.png`. Use this one. |
| `scripts/assemble-video.sh` | Naive concat of every webm in a test output dir. Only for runs without demo mode. |
| `templates/email-login.setup.spec.ts` | Passwordless sign-in via an emailed link read from a test-mail API; saves storageState. |
| `templates/accept-agreements.setup.spec.ts` | One-time first-login dialog for a new demo user. |

## Demo mode

`installDemoMode(page)` patches Playwright's `Locator.prototype` once per worker. That covers
every click in the spec **and** in shared suite helpers it calls, without editing them, and every
page or popup opened later.

| Action | Effect |
|---|---|
| `click`, `dblclick`, `tap`, `check`, `uncheck`, `setChecked`, `selectOption` | Wait for visible, then smooth-scroll to the centre if not fully in view. A cursor glides to the target, a pulsing ring is drawn (around the `<label>` when the input itself is visually hidden), the click ripples, the action runs, then the video holds **3 s**. |
| `fill`, `pressSequentially`, `type` | Same scroll, cursor and ring, then a **1 s** hold. |

- Tunables: `DEMO_CLICK_PAUSE_MS`, `DEMO_TYPE_PAUSE_MS`. Set `DEMO_MODE=0` for a fast functional run while debugging the flow.
- The caller's own `timeout` is respected, so a `click({timeout: 3000})` probe inside try/catch still fails fast.
- The overlay uses `pointer-events: none`, so it never intercepts input. It works for elements inside iframes (Stripe card fields).
- Smoke-test it after any change: `npx playwright test <path>/demoMode.smoke.spec.ts --project=chromium`. It checks the off-screen scroll, the hidden-input label ring and the ≥3 s hold.

## Procedure

1. **Understand the feature from the code.** Read the feature's views and API routes (`how`). Note entry points, feature flags, product codes, emails sent, and anything that books something real with a third party.
2. **Pick an environment where the flow can complete.** A test environment that holds work for manual review, or that has a known bug on the path, will stall the video. Check the tenant settings first.
3. **Sign in without typing a password.** Prefer a saved storageState. For a non-interactive login, use an emailed sign-in link read from the suite's test-mail API (`templates/email-login.setup.spec.ts`). Never hard-code or type a password in a spec.
4. **Walk any unfamiliar screens by hand first,** in a real browser with the same session. Selectors differ between tenants. Only then script them.
5. **Write the scratch spec.**
   - Start from scratch for the app under test. Reuse its patterns: the `mark()` timeline, long pre-click waits, stopping before anything irreversible, and a separate browser context for a second person's view.
   - Call `installDemoMode(page)` first.
   - Use `test.setTimeout(60 * 60 * 1000)`.
   - Put a `mark('<step>')` at each story beat; they are written to `marks.json`.
   - Take screenshots of the key states.
   - Stop before any irreversible real-world action (booking an appointment, a recipient choosing a password).
6. **Give long waits long timeouts.** Demo mode makes a run about 5x longer. Any `waitForEvent`/`waitForResponse` started *before* a run of clicks needs a timeout that covers them. Popups especially: `context.waitForEvent('page', { timeout: 10 * 60 * 1000 }).catch(() => null)`.
7. **Run it in the background,** one spec per job, with output redirected to a log. Don't pipe through `tee`, which hides the exit code. Append `echo EXIT=$?`. Keep any interactive browser on the same account idle while it runs.
8. **When it fails,** read the log, then look at `test-failed-*.png` and `error-context.md` (ARIA snapshot). Fix one cause and re-run.
9. **Find the cut points.** Playwright records one webm per page for that page's whole life. A parent tab that waits while a popup works shows long frozen stretches. Find them with:
   ```bash
   ffmpeg -i video.webm -vf "freezedetect=n=0.01:d=6" -map 0:v -f null - 2>&1 | grep freeze_
   ```
   Confirm with frame grabs (`ffmpeg -ss <t> -i video.webm -frames:v 1 f.png`) and look at them.
10. **Assemble** a full cut and a short cut that starts where the feature itself begins:
    ```bash
    scripts/assemble-segments.sh full.mp4  video.webm:0:67 video-1.webm video.webm:150:194 video-2.webm video-3.webm
    scripts/assemble-segments.sh short.mp4 video-2.webm:336 video-3.webm
    ```
    A video recorded from a *second browser context* (for example a recipient's inbox) lands in its own `recordVideo` dir. Pass that file as a segment.
11. **Check before delivering.** Open each `<out>-contact.png` and confirm the order, that nothing is blank or frozen, and that highlights are visible.
12. **Deliver** both MP4s and the screenshots, with a timeline table from `marks.json` and a list of everything the run created or changed in the test environment.

## Verification checklist

- [ ] The spec passed end to end (exit 0) with demo mode on
- [ ] `demoMode.smoke.spec.ts` passes after any change to `demoMode.ts`
- [ ] Full and short MP4s built; both contact sheets inspected
- [ ] No password, API key or test-mail namespace committed in the spec
- [ ] Nothing irreversible done in a third-party system (no real booking, no recipient sign-up)
- [ ] Delivery lists every record the run created in the test environment

*Last updated: 2026-10-01 | Hub version: 0.12.0*
