#!/bin/sh
# Helper to stage all changes, run tests, and create a draft commit message
pytest -q
if [ $? -ne 0 ]; then
  echo "Tests failed; fix before committing"
  exit 1
fi

git add -A
git commit -m "feat(parashara): derived state, functional-role tables, explainability, tests"

echo "Committed. Create a PR from this branch with the usual workflow."
