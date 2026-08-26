# Fixture: exporter `--force` drops hand-added `references/` files

**Failure class**: `scripts/export_codex_skills.py`'s `export_skills(..., force=True)` deleted
the entire `.grok/skills/<name>/` directory (`shutil.rmtree`) before regenerating it, so any
file under `references/` that was not the generated `source.md` — e.g. a hand-added file like
`grill-with-docs/references/adr-format.md` — was silently deleted and never regenerated.

**Class history (this is what made it REPEAT, not NEW, on its second and third sighting)**:
- Called **NEW**: 2026-08-22, swarm-forge session (`memory-bank/progress.md`, "Housekeeping" bullet)
  — noted as a "pre-existing exporter gap", closed by hand-restoring the two files. No mechanical
  check added.
- Called **REPEAT**: 2026-08-22, PR #9 revision pass 1 (`memory-bank/progress.md`) — same class,
  same two files, closed by hand-restoring again. No mechanical check added.
- Called **REPEAT** again: 2026-08-22, PR #9 revision pass 2 (`memory-bank/progress.md`) —
  explicitly logged as "same pre-existing exporter gap, not fixed here". Still no mechanical
  check.
- This fixture + `tests/test_export_codex_skills.py::test_force_reexport_preserves_hand_added_reference_files`
  + the fix in `scripts/export_codex_skills.py` (`_collect_extra_files` / restore-after-rmtree)
  is what finally closes it: a check that goes red on this exact fixture without the fix, and
  green with it.

## Input fixture

`hand-added-reference.md` in this directory — a stand-in for a file a human adds by hand under
a skill's `references/` directory, alongside the generated `source.md`, that the exporter's
`SKILL_CONFIGS`/`build_skill_markdown` machinery has no knowledge of.

## Expected output

After `export_skills(..., force=True)` runs against an output directory that already contains
this file under `<any-skill>/references/hand-added-reference.md`, the file still exists with
byte-identical content once the re-export finishes.

## Mechanical check

`tests/test_export_codex_skills.py::test_force_reexport_preserves_hand_added_reference_files`:
1. Exports once into a temp directory.
2. Copies this fixture file into `<temp>/grill-with-docs/references/hand-added-reference.md`.
3. Re-exports with `force=True`.
4. Asserts the file still exists with the same content.

Before the fix in `scripts/export_codex_skills.py`, step 4 fails (red) — `shutil.rmtree` in
step 3 deletes the file. After the fix, step 4 passes (green).
