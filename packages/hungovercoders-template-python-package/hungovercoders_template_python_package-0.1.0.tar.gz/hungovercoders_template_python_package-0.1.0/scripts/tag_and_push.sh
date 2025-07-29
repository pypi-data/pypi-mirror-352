#!/usr/bin/env bash
# Tag and push the current version from pyproject.toml

set -e

# TODO: ensure linting, distribution and tests are successful before tagging

PYPROJECT="hungovercoders_repo_tools/pyproject.toml"
VERSION=$(grep '^version' "$PYPROJECT" | head -1 | cut -d '"' -f2)
TAG="v$VERSION"

echo "Detected version: $VERSION"

if git rev-parse "$TAG" >/dev/null 2>&1; then
    echo "Tag $TAG already exists. Deleting..."
    git tag -d "$TAG"
    git push --delete origin "$TAG" || true
fi
git tag "$TAG"
git push origin "$TAG"
echo "Tag $TAG created and pushed."