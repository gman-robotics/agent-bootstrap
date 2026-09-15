# Active Context: Multi-Agent Skills Hub

## Current Focus (This Session)
**GMA-48 leftover follow-up — Blair pass-2 revise** (2026-09-15, cloud agent, branch `cursor/gma-48-leftover-followup-9951`, [PR #18](https://github.com/gman-robotics/agent-bootstrap/pull/18) tip `627b757`). Closed Blair REQUEST_CHANGES theater on companion reverse-pointer validator: bounded `_do_not_use_section` / `_companions_section` parsing (stop at Verification, `---`, or next `##`); hyphen-safe `_mentions_skill` (no `show-me` substring hit inside `show-me-your-work`); require both Do-not-use AND Companions per pair; CLI runs companion checks for `show-me` / `expert-pr-review` outside `PSTACK_SKILL_NAMES`; poison tests both directions strip companion row or Do-not-use cite → fail.

**Verification**: `python3 -m unittest discover -s tests` — 117/117 pass at `627b757`.

**Next**: Blair pass 2; hold merge.
