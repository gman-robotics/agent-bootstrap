"""Mechanical REPEAT-class check: wiki-citation / hoh-plan-wiki-sot.

Failure class: docs/projects/agent-bootstrap/hoh-schema-steal-plan.md's "## 2. Sources"
section cites a public product repository's own GitHub wiki as the *fetched wiki source
of truth* for the `[[harness-of-harness]]` entity, instead of the required internal wiki
SoT.

Called out (as a must-fix, tagged NEW at this first sighting) by Blair grok-4.6's REVISE
on PR #15 (https://github.com/gman-robotics/agent-bootstrap/pull/15) at commit
`d37a75e4`, 2026-09-02. The plan's original §2 cited
`https://github.com/Flesymeb/HarnessOfHarness/wiki/harness-of-harness` (the upstream HoH
product repo's own wiki) as the fetched wiki SoT. The required SoT is:

    ThomasGinter/tmg-wiki, entities/harness-of-harness.md,
    commit 0651e608fded1c0676951ff16555b97e2671710d (short 0651e60, wiki PR #99)

Per triage-review-feedback (skills/triage-review-feedback/SKILL.md Step 3), closing a
REPEAT-class item is never done with an instance fix alone or a plain comment -- this
module is the mechanical check (a real, runnable regression test), not a note. Any
future sighting of this same class (citing a public product repo's own wiki as if it
were the tmg-wiki SoT, for *any* entity page, not just harness-of-harness) is REPEAT
against this class and must be closed the same way: this checker extended, not a new
comment added.

Deliberately scoped to the "## 2. Sources" section only (not the whole document): the
plan's later "## 15." section must be free to *describe* this historical bug in prose
(e.g. in a changelog/proof entry) without that description itself being mistaken for a
live citation. Scoping the check to the actual Sources section is also the more
faithful reading of the review -- the bug is what §2 cites as the fetched wiki SoT, not
whether the literal string ever appears anywhere in the file for any reason.

Run: python3 -m unittest tests.test_hoh_plan_wiki_citation -v
"""
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
PLAN_PATH = REPO_ROOT / "docs" / "projects" / "agent-bootstrap" / "hoh-schema-steal-plan.md"

# The three literals Blair's review requires verbatim in the real plan document's
# Sources section -- either the short SHA plus the full SHA somewhere in the citation,
# or (as landed here) the full SHA alone, which also satisfies "short 0651e60 plus the
# full SHA somewhere".
REQUIRED_WIKI_CITATION_LITERALS = (
    "ThomasGinter/tmg-wiki",
    "entities/harness-of-harness.md",
    "0651e608fded1c0676951ff16555b97e2671710d",
)

# Citing the bare product repo (e.g. "do not clone Flesymeb/HarnessOfHarness", or "do
# not use its wiki as the fetched wiki SoT") is explicitly allowed and must not be
# flagged. Only using *its wiki* as the fetched-wiki-SoT is the bug -- that shape always
# includes this literal substring, on the real product repo's own wiki path.
FORBIDDEN_WIKI_SOT_SUBSTRING = "Flesymeb/HarnessOfHarness/wiki"

_SOURCES_SECTION_RE = re.compile(r"^## 2\. Sources.*?(?=\n## |\Z)", re.DOTALL | re.MULTILINE)


def extract_wiki_sources_section(full_text):
    """Return the '## 2. Sources' section body (from that heading up to the next
    '## ' heading, or end of string if none). Falls back to the whole input when no
    '## 2. Sources' heading is present, so a fixture containing only that section's
    content (no surrounding document) still works unchanged."""
    match = _SOURCES_SECTION_RE.search(full_text)
    return match.group(0) if match else full_text


def find_wiki_citation_violations(full_text):
    """Mechanical check for the wiki-citation / hoh-plan-wiki-sot failure class.

    Scoped to the '## 2. Sources' section only (see module docstring for why).
    Returns an empty list when that section correctly cites all three required
    ThomasGinter/tmg-wiki identity literals and does not use a
    Flesymeb/HarnessOfHarness wiki URL as the fetched wiki source of truth.
    Returns one message per distinct problem found, otherwise.
    """
    section = extract_wiki_sources_section(full_text)
    violations = []
    for literal in REQUIRED_WIKI_CITATION_LITERALS:
        if literal not in section:
            violations.append("missing required wiki-citation literal in Sources section: %r" % (literal,))
    if FORBIDDEN_WIKI_SOT_SUBSTRING in section:
        violations.append(
            "forbidden wiki-sot substring present in Sources section: %r "
            "(the product repo's own wiki must never stand in for the "
            "ThomasGinter/tmg-wiki SoT)" % (FORBIDDEN_WIKI_SOT_SUBSTRING,)
        )
    return violations


# Reproduction of the old, buggy §2 text (trimmed to the load-bearing lines) -- this is
# a fixture of the exact failure class this checker exists to catch, not a hypothetical.
OLD_BUGGY_SECTION_2_FIXTURE = """
## 2. Sources (cited, not recomputed)

- **Wiki**: main `0651e60`, page `[[harness-of-harness]]` = `entities/harness-of-harness.md`
  (landed via PR #99). Fetched via GitHub for this plan
  (`https://github.com/Flesymeb/HarnessOfHarness/wiki/harness-of-harness`, which resolves
  to the repo's README/overview content -- the wiki page and the repo `README.md` carry
  the same HoH overview at the time of this fetch). Repository:
  [`Flesymeb/HarnessOfHarness`](https://github.com/Flesymeb/HarnessOfHarness)
  (MIT licensed, `has_wiki: true`). Not cloned -- read-only citation only.
"""


class WikiCitationMechanicalCheckTests(unittest.TestCase):
    def test_old_fixture_reproduces_the_bug_and_is_caught(self):
        """Red on the old bug: the fixture above must trip the checker."""
        violations = find_wiki_citation_violations(OLD_BUGGY_SECTION_2_FIXTURE)
        self.assertTrue(
            violations,
            "checker must flag the old fixture (Flesymeb wiki cited as the fetched "
            "wiki SoT, real tmg-wiki literals absent) -- got zero violations",
        )
        joined = " ".join(violations)
        self.assertIn(
            "ThomasGinter/tmg-wiki", joined,
            "the missing-required-literal violation must name the real SoT repo",
        )
        self.assertIn(
            FORBIDDEN_WIKI_SOT_SUBSTRING, joined,
            "the forbidden-substring violation must name the exact bad URL shape",
        )

    def test_a_fixed_but_incomplete_citation_is_still_caught(self):
        """Removing the forbidden URL alone (without adding the real citation) must
        still fail -- this guards against a shallow fix that deletes the bad line
        without landing the required tmg-wiki identity."""
        incomplete_fix = OLD_BUGGY_SECTION_2_FIXTURE.replace(
            "https://github.com/Flesymeb/HarnessOfHarness/wiki/harness-of-harness",
            "https://github.com/Flesymeb/HarnessOfHarness",
        )
        violations = find_wiki_citation_violations(incomplete_fix)
        self.assertTrue(
            violations,
            "removing only the forbidden URL, with no tmg-wiki citation added, "
            "must still be flagged as missing the required literals",
        )

    def test_real_plan_document_cites_the_required_wiki_sot(self):
        """Green on the real, current plan doc's Sources section: every required
        literal present, the forbidden substring absent -- scoped to '## 2. Sources'
        so this does not trip on a later section merely discussing the old bug."""
        self.assertTrue(PLAN_PATH.exists(), "plan doc not found at %s" % (PLAN_PATH,))
        text = PLAN_PATH.read_text(encoding="utf-8")
        violations = find_wiki_citation_violations(text)
        self.assertEqual(
            violations,
            [],
            "real plan document's Sources section must cite ThomasGinter/tmg-wiki as "
            "the wiki SoT with no leftover Flesymeb-wiki-as-SoT citation; "
            "violations: %s" % (violations,),
        )

    def test_real_plan_document_may_still_name_the_bare_product_repo_as_a_leftover(self):
        """Naming the bare product repo (no /wiki suffix) as a do-not-clone leftover,
        anywhere in the document, is explicitly allowed and must not itself trip the
        forbidden-substring check."""
        text = PLAN_PATH.read_text(encoding="utf-8")
        self.assertIn(
            "Flesymeb/HarnessOfHarness", text,
            "the plan should still name the product repo as a do-not-clone leftover",
        )

    def test_real_plan_document_may_discuss_the_old_bug_outside_the_sources_section(self):
        """A later section (e.g. a changelog/proof entry) may describe the historical
        bug using the exact forbidden URL shape in prose without being mistaken for a
        live citation -- the check is scoped to '## 2. Sources' only, not the whole
        document, precisely so this is possible."""
        text = PLAN_PATH.read_text(encoding="utf-8")
        sources_section = extract_wiki_sources_section(text)
        self.assertNotIn(FORBIDDEN_WIKI_SOT_SUBSTRING, sources_section)
        # This assertion is deliberately not "assertNotIn(..., text)" -- see docstring.


if __name__ == "__main__":
    unittest.main()
