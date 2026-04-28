# Cherry-Pick to Release Branch Workflow

This workflow automates cherry-picking changes from a merged PR into an existing release branch and incrementing the release candidate version suffix.

## Parameters
- **RELEASE_BRANCH**: The release branch name (e.g., `releases/2026.03.24`)
- **PR_NUMBER**: The GitHub PR number whose commits should be cherry-picked (e.g., `4256`)
- **VERSION_FILES**: A space-separated list of JSON files where the version string should be updated (e.g., `package.json apps/web/package.json`)

## Prerequisites
- Git repository cloned locally and remote `origin` configured.
- The release branch must already exist on the remote.
- The PR must already be merged (commits are available on the remote).

## Steps

1. **Fetch and Checkout the Release Branch**
   ```bash
   git fetch origin ${RELEASE_BRANCH}
   git checkout ${RELEASE_BRANCH}
   ```

2. **Identify the PR Commits**
   - Use the GitHub MCP tool (`pull_request_read` with method `get`) to get the PR details, specifically the `head.sha` and the base SHA.
   - Fetch the PR head ref to make commits locally available:
     ```bash
     git fetch origin refs/pull/${PR_NUMBER}/head
     ```
   - List the commits between the PR base and head to identify the individual SHAs:
     ```bash
     git log FETCH_HEAD --oneline -10
     ```
   - Identify which commits belong to the PR (commits after the base SHA, up to and including the head SHA).

3. **Cherry-Pick the Commits**
   - Cherry-pick all PR commits in order (oldest first):
     ```bash
     git cherry-pick <first-commit-sha> <second-commit-sha> ...
     ```
   - If conflicts arise, resolve them manually, then `git cherry-pick --continue`.

4. **Determine Current Version**
   - Read the current version from the primary release file (usually the first file in `VERSION_FILES`):
     ```bash
     grep '"version"' $(echo $VERSION_FILES | awk '{print $1}')
     ```
   - Note the current version string (e.g., `2026.03.24-build.002`).

5. **Determine the New RC Version**
   - Inspect the current version string:
     - If it already contains `-rc.N` (e.g., `2026.03.24-build.002-rc.2`), increment N by 1 → `-rc.3`.
     - If it does **not** contain `-rc.N` (e.g., `2026.03.24-build.002`), append `-rc.2`.
   - Compute using bash:
     ```bash
     CURRENT_VERSION=$(node -p "require('./' + '$(echo $VERSION_FILES | awk '{print $1}')').version")
     if [[ "$CURRENT_VERSION" =~ -rc\.([0-9]+)$ ]]; then
       RC_NUM=$(( ${BASH_REMATCH[1]} + 1 ))
       BASE_VERSION="${CURRENT_VERSION%-rc.*}"
     else
       RC_NUM=2
       BASE_VERSION="$CURRENT_VERSION"
     fi
     NEW_VERSION="${BASE_VERSION}-rc.${RC_NUM}"
     ```

6. **Update Version Strings**
   - Apply the new version to all `VERSION_FILES`:
     ```bash
     for file in $VERSION_FILES; do
       sed -i '' "s/\"version\": \"${CURRENT_VERSION}\"/\"version\": \"${NEW_VERSION}\"/" $file
     done
     ```
   - Verify:
     ```bash
     grep '"version"' $VERSION_FILES
     ```

7. **Commit the Version Bump**
   ```bash
   git add $VERSION_FILES
   git commit -m "VERSION UPDATE: ${NEW_VERSION}"
   ```

8. **Push to Remote**
   ```bash
   git push origin ${RELEASE_BRANCH}
   ```

9. **Verify**
   ```bash
   git log --oneline -5
   git status
   ```

## Example Usage

Cherry-pick PR #4256 into `releases/2026.03.24`:
- `RELEASE_BRANCH` = `releases/2026.03.24`
- `PR_NUMBER` = `4256`
- `VERSION_FILES` = `package.json packages/api/package.json`

**Scenario A** — No RC suffix yet (version is `2026.03.24-build.002`):
Result: `2026.03.24-build.002` → `2026.03.24-build.002-rc.2`

**Scenario B** — RC already present (version is `2026.03.24-build.002-rc.2`):
Result: `2026.03.24-build.002-rc.2` → `2026.03.24-build.002-rc.3`

## Notes
- The version on the release branch may differ from `main` — always read it from the checked-out branch, not from memory.
- If the PR had multiple commits (visible in PR details as `commits: N`), cherry-pick all of them in chronological order.
- GitHub branch protection rules on release branches may produce a warning about bypassing PR requirements when pushing directly — this is expected for release branch maintenance.
- Do **not** cherry-pick version bump commits from main (e.g., `VERSION UPDATE: ...`) — only cherry-pick the feature/fix commits from the PR.

Last updated: 2026-03-25
