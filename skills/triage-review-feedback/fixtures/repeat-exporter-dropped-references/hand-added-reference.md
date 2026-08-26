# Hand-added reference fixture

Stand-in for a file a human adds by hand under a skill's `references/` directory (for example
`grill-with-docs/references/adr-format.md`) that the exporter's generated `SKILL.md` /
`source.md` pair does not know about. This exact file must survive a `force=True` re-export of
`scripts/export_codex_skills.py` byte-for-byte — see `README.md` in this directory.
