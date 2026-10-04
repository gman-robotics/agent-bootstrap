---
name: benchmark-checklist
description: "Vet a performance number before reporting or acting on it. Limiter, tuning, limits, errors, repeat runs, end-to-end relevance, and proof the work happened. Use for /benchmark-checklist or any speedup or regression claim."
version: 1.0.0
---

# benchmark-checklist

**Purpose**
Refuse a performance number that cannot name its limiter. This is the gate `performance-profiling` was missing.

**Trigger**
"/benchmark-checklist", a before/after claim, a regression claim, or a choice between implementations based on a measurement.

**Do not use for**
- Finding the slow path in the first place → `performance-profiling` (call this skill on every number that playbook reports)
- A one-run ballpark the user explicitly asked for → still answer questions 4 and 7, say it is one run, and skip the rest unless the run looks wrong. A choice between options is never a ballpark.

## Companions

| Skill | Role here |
|---|---|
| `performance-profiling` | Finds and fixes slowness; this skill vets its baseline and every number after |
| `pstack-principles` | explain-the-number is the standing rule behind this checklist |
| `show-me-your-work` | Commit the run log when the decision must be reviewable |

**Verification**
- The claim sentence was written before the reported runs
- Verdict is faster, slower, no measurable difference, or inconclusive
- Inconclusive if the limiter is unnamed, a side ran untuned, or questions 4 and 7 were not checked
- Report includes unit, run count, range, and limiter

---

# Benchmark checklist

Answer each question from a run, not from a guess about the code. Cite `pstack-principles` (explain-the-number).

## Before you run

- Write the claim in the words you would ship ("export is 30% faster at p50 on the 60k-row dataset").
- Read the measurement script. Note what it times, what it counts, and what it ignores.
- Check load average (`uptime`) and core count (`nproc`). If the machine is busy, interleave the sides and say so.

## Questions

1. **Why not double?** Name the limiter from a profile you do not report (profilers slow the work). Watch the load generator. If a change did not move the number, the limiter explains why.
2. **Was it tuned?** Release builds, production flags, warm or cold caches as production sees them, same versions and data. A commit-per-row, a debug build, or a missing index means that side is untuned. Tune and measure again before you pick a winner.
3. **Did it break limits?** Bytes per second versus disk and network. Time saved versus time the changed piece took. Removing a piece that takes 10% of the run can make the run at most about 11% faster.
4. **Did it error?** Count failures. Errors are often fast. If the script does not count them, add the count.
5. **Does it reproduce?** At least 5 runs per side, alternating sides. Report median and range. A gap smaller than run-to-run variation is no measurable difference.
6. **Does it matter?** Next to any micro result, measure the end-to-end path a user waits on. Report the micro result as a share of the whole.
7. **Did it even happen?** The request reached the server, the rows were written, the code used the result. Lazy code and timeouts produce numbers for work that never ran.

## Report

Lead with the verdict. Give the number, unit, run count, range, and limiter. Keep a PR body to one primary number. Put the runs in a linked artifact.

## Provenance

Adapted from [cursor/plugins/pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT), pstack 0.15.9 (2026-10-03). Native multi-harness hub playbook — not a marketplace plugin copy. Cursor-only harness names stripped per `skills/subagent-routing/SKILL.md`.

*Last updated: 2026-10-03 | Hub version: 0.12.0*

