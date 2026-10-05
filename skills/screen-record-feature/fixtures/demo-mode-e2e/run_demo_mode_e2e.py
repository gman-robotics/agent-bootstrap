#!/usr/bin/env python3
"""Live gate for screen-record-feature: run the skill's real recording tooling end to end.

No app, login or network service is involved, so this runs anywhere with Node + ffmpeg:

1. Copy the skill's real `scripts/demoMode.ts` and `scripts/demoMode.smoke.spec.ts` into a
   throwaway Playwright project (temp dir) and install `@playwright/test` there.
2. Run the smoke spec with video on. It asserts, against a real Chromium page, that an
   off-screen target is scrolled into view before the click, that a visually-hidden radio
   is checked through its label, that the click holds for at least 3 s, and it captures a
   mid-click screenshot.
3. Check that the screenshot really shows the overlay (the orange highlight-ring pixels).
4. Build an MP4 from two time ranges of the recorded webm with the skill's real
   `scripts/assemble-segments.sh`, and check that the MP4 and its contact sheet exist and that
   the duration matches the requested segments.

Prints `OK: screen-record-feature demo-mode-e2e` on success. Exit codes: 0 pass, 1 fail,
2 blocked (node/npx/ffmpeg missing, or the Playwright install could not be completed).
"""
from __future__ import annotations

import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
SKILL_DIR = REPO_ROOT / "skills" / "screen-record-feature"
PLAYWRIGHT_VERSION = os.environ.get("SRF_PLAYWRIGHT_VERSION", "1.55.1")
RING_RGB = (245, 158, 11)  # #f59e0b, the demoMode ring colour


def blocked(msg: str) -> None:
    print(f"BLOCKED: {msg}")
    sys.exit(2)


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    sys.exit(1)


def run(cmd: list[str], cwd: Path, timeout: int, env: dict | None = None) -> subprocess.CompletedProcess:
    print("$", " ".join(cmd))
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout,
                          env={**os.environ, **(env or {})})


def find_ffmpeg() -> str | None:
    if os.environ.get("FFMPEG"):
        return os.environ["FFMPEG"]
    found = shutil.which("ffmpeg")
    if found:
        return found
    # Playwright ships its own ffmpeg build for video encoding; it only encodes VP8, so it is
    # not used for MP4 assembly. A real ffmpeg is required.
    return None


def png_has_ring_pixels(png: Path, min_pixels: int = 40) -> int:
    """Count pixels close to the ring colour in an 8-bit RGB/RGBA PNG (no third-party deps)."""
    data = png.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        fail(f"{png} is not a PNG")
    pos, width, height, color_type, idat = 8, 0, 0, 0, b""
    while pos < len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        if ctype == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", body[:10])
            if bit_depth != 8 or color_type not in (2, 6):
                fail(f"unexpected PNG format bit_depth={bit_depth} color_type={color_type}")
        elif ctype == b"IDAT":
            idat += body
        pos += 12 + length
    bpp = 4 if color_type == 6 else 3
    raw = zlib.decompress(idat)
    stride = width * bpp
    prev = bytearray(stride)
    hits, i = 0, 0
    for _ in range(height):
        ftype = raw[i]
        line = bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):
            a = line[x - bpp] if x >= bpp else 0
            b = prev[x]
            c = prev[x - bpp] if x >= bpp else 0
            if ftype == 1:
                line[x] = (line[x] + a) & 0xFF
            elif ftype == 2:
                line[x] = (line[x] + b) & 0xFF
            elif ftype == 3:
                line[x] = (line[x] + ((a + b) >> 1)) & 0xFF
            elif ftype == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                line[x] = (line[x] + pred) & 0xFF
        for x in range(0, stride, bpp):
            r, g, bl = line[x], line[x + 1], line[x + 2]
            if abs(r - RING_RGB[0]) < 30 and abs(g - RING_RGB[1]) < 40 and abs(bl - RING_RGB[2]) < 40:
                hits += 1
        prev = line
    return hits


def main() -> None:
    for tool in ("node", "npx"):
        if not shutil.which(tool):
            blocked(f"{tool} not found on PATH")
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        blocked("ffmpeg not found (install it or set FFMPEG=/path/to/ffmpeg)")

    work = Path(tempfile.mkdtemp(prefix="srf-e2e-"))
    try:
        for name in ("demoMode.ts", "demoMode.smoke.spec.ts"):
            shutil.copy(SKILL_DIR / "scripts" / name, work / name)
        (work / "package.json").write_text('{"name":"srf-e2e","private":true}\n')
        (work / "playwright.config.ts").write_text(
            "import { defineConfig } from '@playwright/test';\n"
            "export default defineConfig({ testDir: '.', testMatch: /demoMode\\.smoke\\.spec\\.ts/,\n"
            "  timeout: 120000, use: { browserName: 'chromium' } });\n"
        )
        inst = run(["npm", "install", "--no-audit", "--no-fund", "--silent",
                    f"@playwright/test@{PLAYWRIGHT_VERSION}"], work, 600)
        if inst.returncode != 0:
            blocked(f"npm install @playwright/test failed: {inst.stderr[-400:]}")
        br = run(["npx", "playwright", "install", "chromium"], work, 900)
        if br.returncode != 0:
            blocked(f"playwright browser install failed: {br.stderr[-400:]}")

        out_dir = work / "out"
        test = run(["npx", "playwright", "test", "--reporter=line", f"--output={out_dir}"], work, 600)
        print(test.stdout[-1500:])
        if test.returncode != 0:
            fail(f"demoMode smoke spec failed (exit {test.returncode}): {test.stderr[-800:]}")
        if "[demoMode] on" not in test.stdout:
            fail("demo mode did not report installing itself")
        m = re.search(r'"firstClickMs":(\d+)', test.stdout)
        if not m or int(m.group(1)) < 3000:
            fail(f"click hold under 3 s: {m.group(0) if m else 'no timing printed'}")
        print(f"click hold: {m.group(1)} ms")

        shots = list(out_dir.rglob("mid-click.png"))
        videos = list(out_dir.rglob("video.webm"))
        if not shots or not videos:
            fail(f"missing artefacts: screenshots={shots} videos={videos}")
        ring = png_has_ring_pixels(shots[0])
        if ring < 40:
            fail(f"highlight ring not visible in mid-click screenshot ({ring} ring-coloured pixels)")
        print(f"ring pixels in mid-click screenshot: {ring}")

        mp4 = work / "assembled.mp4"
        asm = run(["bash", str(SKILL_DIR / "scripts" / "assemble-segments.sh"), str(mp4),
                   f"{videos[0]}:0:4", f"{videos[0]}:6:9"], work, 300, env={"FFMPEG": ffmpeg})
        print(asm.stdout[-600:])
        if asm.returncode != 0:
            fail(f"assemble-segments.sh failed (exit {asm.returncode}): {asm.stderr[-600:]}")
        sheet = work / "assembled-contact.png"
        if not mp4.is_file() or mp4.stat().st_size < 10_000 or not sheet.is_file():
            fail("assemble-segments.sh did not produce the MP4 and contact sheet")
        d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", asm.stdout)
        secs = (int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3))) if d is not None else -1.0
        if not 6.0 <= secs <= 8.0:
            fail(f"assembled duration {secs}s, expected about 7s (4s + 3s segments)")
        print(f"assembled mp4: {mp4.stat().st_size} bytes, {secs:.2f}s")
        print("OK: screen-record-feature demo-mode-e2e")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
