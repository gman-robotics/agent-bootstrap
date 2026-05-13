#!/bin/sh
# check-tdd.sh — TDD Pre-Commit Warning Hook
#
# Warns when source files are staged without any test file changes, enforcing
# the Red/Green/Refactor standard defined in docs/shared/tdd-standard.md.
#
# INSTALL (run from within the target project repo):
#   cp ../agent-bootstrap/scripts/check-tdd.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#
# MODE:
#   Default: warning-only (exit 0) — commit proceeds, developer is reminded.
#   To make it blocking: change the final "exit 0" to "exit 1".
#   Bypass when needed: git commit --no-verify

staged=$(git diff --cached --name-only --diff-filter=ACM 2>/dev/null)

# Source files: .ts .tsx .js .jsx .py — excluding test files
source_files=$(echo "$staged" | grep -E '\.(ts|tsx|js|jsx|py)$' | grep -vE '(\.test\.|\.spec\.|_test\.|/tests?/|/test/|__tests__)' | grep -v '^$')

# Test files
test_files=$(echo "$staged" | grep -E '(\.test\.|\.spec\.|_test\.|/tests?/|/test/|__tests__)' | grep -v '^$')

if [ -n "$source_files" ] && [ -z "$test_files" ]; then
  printf "\n\033[33m⚠  TDD WARNING\033[0m  Source files staged without any test file changes.\n\n"
  printf "Staged source files:\n"
  echo "$source_files" | sed 's/^/  /'
  printf "\nPer \033[36mdocs/shared/tdd-standard.md\033[0m, all non-trivial logic requires a\n"
  printf "failing test written *before* the production code (Red/Green/Refactor).\n\n"
  printf "If this is intentional (glue code, config, type definitions, docs),\n"
  printf "the commit can proceed as-is.\n"
  printf "To skip this check entirely: \033[36mgit commit --no-verify\033[0m\n\n"
fi

# Change to "exit 1" to make this hook blocking instead of advisory.
exit 0
