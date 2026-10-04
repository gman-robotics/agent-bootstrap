---
name: split-branch-for-pr
description: "This skill should be used when work has landed on a branch mixed in with unrelated commits (e.g. a long-lived feature branch that accumulated other fixes over time) and needs to be split into a clean PR against the default branch. Cherry-picks only the relevant commits onto a fresh branch off the target, detects and strips out unrelated changes that got accidentally swept into a shared commit, opens the PR, and optionally resets the original branch to drop the now-duplicated history. Trigger phrases: 'split this work into its own branch/PR', 'clean up this branch before PR', 'this branch has unrelated stuff mixed in'."
version: 1.0.0
---

# Split Branch for PR Workflow

Pulls a specific piece of work off a messy branch (mixed with unrelated commits, or commits that accidentally swept in unrelated file changes) and lands it as a clean, reviewable PR — without rewriting the commits that already exist elsewhere, and without silently carrying unrelated diffs into the new PR.

## When to Use

- A feature/fix branch has drifted to include unrelated work (its own commits, or commits shared with other unrelated changes) and the user wants just one piece of it split out for its own PR.
- A commit turns out to have swept in accidental unrelated file changes (config, infra, unrelated docs) that don't belong in the PR being prepared.

## Prerequisites

- Git repository with the messy branch already checked out or fetched locally.
- Know which commits (or which file paths) constitute "the work" to split out, versus what's unrelated.

## Steps

1. **Identify the commit range ahead of the target branch**
   ```bash
   git fetch origin <target-branch> -q
   git log --oneline --reverse origin/<target-branch>..<messy-branch>
   ```
   List commits oldest-first. Classify each as: relevant (keep), a hard dependency of a relevant commit (keep), or unrelated (skip).

2. **Inspect any commit that might carry a dependency**
   For any commit the relevant work imports/relies on (e.g. a shared library, schema, or harness it reads from), check its diff stat before deciding to include it:
   ```bash
   git show --stat <sha>
   ```

3. **Create the new branch from the target, not from the messy branch**
   ```bash
   git checkout -b <new-branch> origin/<target-branch>
   ```
   Starting from the target (not the messy branch) guarantees nothing unrelated rides along implicitly.

4. **Cherry-pick the relevant commits in chronological order**
   ```bash
   git cherry-pick <sha1> <sha2> <sha3>
   ```
   Resolve any conflicts, then `git add <file> && git cherry-pick --continue`. For conflicts in unrelated tracked files (e.g. a shared log/doc file), prefer keeping the target branch's version (`git checkout --ours <file>`) unless the conflicting content is itself part of the work being split out. If a file shows `gitignore`-related "ignored by one of your .gitignore files" errors on `git add` even though it's already tracked, use `git add -f`.

5. **Diff the full new branch against the target to catch swept-in unrelated changes**
   ```bash
   git diff --stat origin/<target-branch>..HEAD | tail -5
   git diff --name-only origin/<target-branch>..HEAD | sed -E 's#/.*##' | sort -u
   ```
   Scan the top-level directories/files touched. Anything that doesn't obviously belong to the work being split out is a candidate for accidental inclusion — inspect its actual diff:
   ```bash
   git diff origin/<target-branch>..HEAD -- <suspicious-path>
   ```

6. **Strip out anything unrelated via follow-up commits — never rewrite the cherry-picked commits**
   ```bash
   git checkout origin/<target-branch> -- <unrelated-file-to-revert>
   git rm <unrelated-file-to-remove>
   git commit -m "Revert/drop unrelated <X> picked up by an earlier commit"
   ```
   Keeping this as a separate commit (rather than amending/rebasing the cherry-picked ones) preserves an honest history and avoids fighting cherry-pick metadata.

7. **Re-verify scope, then typecheck/test if applicable**
   Repeat step 5 until the diff only contains directories/files that belong to the work. Run the project's typecheck/test commands before pushing.

8. **Push and open the PR**
   ```bash
   git push -u origin <new-branch>
   gh pr create --title "..." --body "..."
   ```
   Write the PR body to name what was pulled out, and call out any cleanup commits (step 6) so reviewers understand why the diff includes small unrelated-looking reverts.

9. **Optionally reset the original messy branch to remove the now-duplicated commits**
   Only if the user explicitly confirms — this rewrites already-pushed remote history:
   ```bash
   git branch -f <messy-branch> <last-good-sha-before-the-split-work>
   git push --force-with-lease origin <messy-branch>
   ```
   `--force-with-lease` (not `--force`) protects against clobbering someone else's concurrent push. Confirm with the user before every force-push — this is a destructive/irreversible-feeling action even though the work is safely preserved on the new branch.

## Notes

- Never use `git rebase -i` or amend the cherry-picked commits to "clean them up" — a follow-up commit is safer, auditable, and doesn't require force-pushing the *new* branch.
- If the messy branch has an upstream and other agents/processes may push to it concurrently, re-fetch immediately before step 9's `git branch -f` to avoid resetting past someone else's new work.
- A commit that already exists on the target branch's history should not be re-picked — check with `git merge-base --is-ancestor <sha> origin/<target-branch>` first if unsure.
