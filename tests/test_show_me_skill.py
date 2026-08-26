import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SHOW_ME_SKILL_MD = REPO_ROOT / "skills" / "show-me" / "SKILL.md"
REPLY_CONTRACT_SKILL_MD = REPO_ROOT / "skills" / "reply-contract" / "SKILL.md"
PHOTON_SHOW_ME_MD = REPO_ROOT / "skills" / "reply-contract" / "references" / "photon-show-me.md"
GROK_SHOW_ME_SKILL_MD = REPO_ROOT / ".grok" / "skills" / "show-me" / "SKILL.md"
GROK_SHOW_ME_SOURCE_MD = REPO_ROOT / ".grok" / "skills" / "show-me" / "references" / "source.md"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.index_skills import GRANDFATHERED_SKILLS  # noqa: E402

REAL_PATH_TOKEN = "skills/show-me/SKILL.md"
FICTIONAL_PAIRING_LINE = "Pair with **show-me** (trees / stacks / diffs)."

# --- Photon-safe content scanner ----------------------------------------------------
#
# REPEAT review finding on this PR (same class as PR #11 blocker #3, "reading the skill
# Markdown is not a pass"): the prior fixture only asserted headings/paths/frontmatter
# via read_text() -- a SKILL.md that recommended `Bash(open file.html)` or made
# mermaid/HTML the default visual would still pass every one of those tests. This
# scanner is a real, run-it mechanical check of SKILL.md *content*, not its shape.
#
# It first splits the file into markdown "units" (one bullet/numbered item, or one
# blank-line-delimited paragraph, tagged with its nearest `##` heading) so that one
# bullet's negation word (e.g. "never") cannot leak into a *different* bullet and mask
# a violation there -- a plain character-radius window was tried first and failed
# exactly this way (see memory-bank/progress.md for the reproduction). Each unit is
# then checked for a forbidden-guidance pattern (recommending an HTML/browser open, a
# `Bash(open ...)` command, or mermaid/HTML framed as the default visual); a match only
# counts as a violation if that unit plus its heading contains no negation marker
# (`never`, `no `, `without`, `opt-in`, `only if`, `pitfall`, ...). A forbidding bullet
# (what the real file contains) carries its own negation marker and does not trip the
# check; a recommending bullet (the violating case this exists to catch) has none and
# does.
NEGATION_MARKERS = (
    "never", "no ", "not ", "n't", "without", "opt-in", "avoid", "forbid",
    "pitfall", "only if", "unless",
)
_OPEN_HTML_PATTERN = re.compile(r"(open|launch\w*)\b.{0,60}\b(html|browser)\b", re.IGNORECASE)
_BASH_OPEN_PATTERN = re.compile(r"bash\(\s*open", re.IGNORECASE)
_DEFAULT_MERMAID_HTML_PATTERN = re.compile(
    r"\bdefault\b.{0,60}\b(mermaid|html)\b|\b(mermaid|html)\b.{0,60}\bdefault\b",
    re.IGNORECASE,
)
_HEADING_PATTERN = re.compile(r"^#{1,6}\s+(.*)$")
_LIST_ITEM_PATTERN = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def _iter_markdown_units(skill_text: str) -> list[tuple[str, str]]:
    """Split `skill_text` into (nearest_heading, unit_text) pairs.

    A unit is one markdown list item or one blank-line-delimited paragraph -- the
    smallest grain the source actually uses -- so two independent bullets are never
    merged into a single negation-context window.
    """
    units: list[tuple[str, str]] = []
    heading = ""
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            units.append((heading, " ".join(buffer).strip()))
            buffer.clear()

    for line in skill_text.splitlines():
        stripped = line.strip()
        heading_match = _HEADING_PATTERN.match(stripped)
        if heading_match:
            flush()
            heading = heading_match.group(1)
            continue
        if not stripped:
            flush()
            continue
        if _LIST_ITEM_PATTERN.match(stripped):
            flush()
            buffer.append(stripped)
            continue
        buffer.append(stripped)
    flush()
    return units


def find_photon_safe_violations(skill_text: str) -> list[str]:
    """Return one message per forbidden-guidance unit with no nearby negation marker.

    An empty list is the pass case. This is the mechanical check itself -- called
    against real file content below, never just described in a docstring.
    """
    violations: list[str] = []
    checks = (
        (_OPEN_HTML_PATTERN, "recommends opening HTML/a browser for the human"),
        (_BASH_OPEN_PATTERN, "recommends a Bash(open ...) command"),
        (_DEFAULT_MERMAID_HTML_PATTERN, "treats mermaid/HTML as the default visual"),
    )
    for heading, unit in _iter_markdown_units(skill_text):
        negation_context = f"{heading} {unit}".lower()
        for pattern, label in checks:
            if pattern.search(unit) and not any(
                marker in negation_context for marker in NEGATION_MARKERS
            ):
                violations.append(f"{label} (under heading {heading!r}): {unit!r}")
    return violations


# The "old case" this check exists to catch: a SKILL.md that treats mermaid/HTML as the
# default visual and recommends a `Bash(open ...html)` command to show it to the human
# -- precisely the two shapes the review named as unguarded by the previous
# heading-only unittest, formatted as the same kind of bullet list the real file uses.
# Not hypothetical: `find_photon_safe_violations` is run against this literal string in
# `test_find_photon_safe_violations_catches_the_old_fictional_case` below and is
# required to return violations, proving the check goes red on this class before it is
# ever trusted to stay green on the real, committed file.
OLD_FICTIONAL_CASE_SKILL_TEXT = """
## One primary visual per reply

- Default visual: a mermaid diagram or an HTML dashboard, built for every reply.
- After building the diagram, open it for the user with `Bash(open diagram.html)` so
  they can see it.
"""


class ShowMeSkillTests(unittest.TestCase):
    """Mechanical check that show-me exists and reply-contract's pairing line
    points at the real skill path, not a fictional name.

    This is the black-box-agent-qa evidence for this skill: the task requirement
    ("reply-contract keeps voice ... it LOADS skills/show-me/SKILL.md for the one
    visual. Change the pairing line from fiction to a real path.") is a literal,
    checkable fact about the committed files, not a description of intent.
    """

    def test_show_me_skill_file_exists(self) -> None:
        self.assertTrue(
            SHOW_ME_SKILL_MD.is_file(), f"missing {SHOW_ME_SKILL_MD}"
        )

    def test_show_me_frontmatter_declares_the_skill_name_and_version(self) -> None:
        text = SHOW_ME_SKILL_MD.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: show-me\n"))
        self.assertIn("version: 1.0.0", text)

    def test_reply_contract_pairing_line_points_at_the_real_show_me_path(self) -> None:
        text = REPLY_CONTRACT_SKILL_MD.read_text(encoding="utf-8")
        self.assertIn(
            REAL_PATH_TOKEN,
            text,
            "reply-contract must reference the real skills/show-me/SKILL.md path",
        )
        self.assertNotIn(
            FICTIONAL_PAIRING_LINE,
            text,
            "old fictional pairing line (no real path) must be gone",
        )

    def test_reply_contract_loads_show_me_rather_than_reimplementing_it(self) -> None:
        text = REPLY_CONTRACT_SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("Load `skills/show-me/SKILL.md`", text)

    def test_photon_show_me_reference_points_at_the_real_skill_path(self) -> None:
        text = PHOTON_SHOW_ME_MD.read_text(encoding="utf-8")
        self.assertIn(REAL_PATH_TOKEN, text)

    def test_show_me_is_exported_to_the_grok_dual_tree(self) -> None:
        self.assertTrue(
            GROK_SHOW_ME_SKILL_MD.is_file(),
            f"missing {GROK_SHOW_ME_SKILL_MD} — run "
            "scripts/export_codex_skills.py --output-dir .grok/skills --force",
        )
        grok_text = GROK_SHOW_ME_SKILL_MD.read_text(encoding="utf-8")
        self.assertTrue(grok_text.startswith("---\nname: show-me\n"))

        # Pins the other half of the dual tree: the exporter also writes a
        # references/source.md copy of the canonical SKILL.md (footer's "Last updated"
        # line stripped by design, see scripts/export_codex_skills.strip_trailing_footer)
        # next to the thin wrapper above. Nothing previously asserted this file exists.
        self.assertTrue(
            GROK_SHOW_ME_SOURCE_MD.is_file(),
            f"missing {GROK_SHOW_ME_SOURCE_MD} — run "
            "scripts/export_codex_skills.py --output-dir .grok/skills --force",
        )
        source_text = GROK_SHOW_ME_SOURCE_MD.read_text(encoding="utf-8")
        self.assertIn("## Recipe: call tree", source_text)
        self.assertNotIn("Last updated:", source_text.splitlines()[-1])

    def test_show_me_is_not_grandfathered_into_the_live_gate(self) -> None:
        """show-me is a brand-new skill; it must earn its own black-box-agent-qa pass
        rather than being exempted via scripts/index_skills.GRANDFATHERED_SKILLS."""
        self.assertNotIn("show-me", GRANDFATHERED_SKILLS)

    def test_skill_never_recommends_opening_html_or_defaulting_to_mermaid_html(self) -> None:
        """Photon-safe I/O check (must-fix REPEAT close): run the mechanical scanner
        against the real, committed SKILL.md content -- not a heading/path grep, an
        actual pass/fail evaluation of what the file recommends. Must return no
        violations."""
        text = SHOW_ME_SKILL_MD.read_text(encoding="utf-8")
        violations = find_photon_safe_violations(text)
        self.assertEqual(
            violations,
            [],
            "skills/show-me/SKILL.md recommends opening HTML/a browser, or treats "
            "mermaid/HTML as a default visual: " + "; ".join(violations),
        )

    def test_find_photon_safe_violations_catches_the_old_fictional_case(self) -> None:
        """Proves the check above is not vacuous: run it against a synthetic fixture of
        the exact violating shape (mermaid/HTML as default + a Bash(open ...html)
        command) and require it to fail loudly (non-empty violations) -- the check goes
        red on that case, it does not pass everything unconditionally."""
        violations = find_photon_safe_violations(OLD_FICTIONAL_CASE_SKILL_TEXT)
        self.assertTrue(
            violations,
            "the photon-safe checker must flag a SKILL.md that recommends opening "
            "HTML or defaults to mermaid/HTML — got no violations on the known-bad case",
        )
        joined = " ".join(violations).lower()
        self.assertIn("default", joined)
        self.assertIn("open", joined)

    def test_show_me_owns_the_visual_recipes_not_reply_contract(self) -> None:
        """show-me is a fold of recipes only — it is not a rewrite of reply-contract's
        voice/marks/leftover-vs-bug/spec-gate/clarify/task-name machinery."""
        show_me_text = SHOW_ME_SKILL_MD.read_text(encoding="utf-8")
        reply_contract_text = REPLY_CONTRACT_SKILL_MD.read_text(encoding="utf-8")

        for recipe_marker in ("## Recipe: call tree", "## Recipe: file/screen tree", "## Recipe: stack"):
            self.assertIn(recipe_marker, show_me_text)

        for reply_contract_only_marker in ("## Voice", "## Task name", "### Spec-gate card"):
            self.assertIn(reply_contract_only_marker, reply_contract_text)
            self.assertNotIn(reply_contract_only_marker, show_me_text)


if __name__ == "__main__":
    unittest.main()
