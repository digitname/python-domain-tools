#!/bin/bash

# Function to extract the latest version from CHANGELOG.md
get_latest_version() {
    grep -m 1 "## \[" CHANGELOG.md | sed 's/## \[//;s/\].*//'
}

# Get the latest version
VERSION=$(get_latest_version)

# Check if we got a version
if [ -z "$VERSION" ]; then
    echo "Error: Could not find a version in CHANGELOG.md"
    exit 1
fi

# Get the changelog entry for the latest version
CHANGELOG_ENTRY=$(sed -n "/## \[$VERSION\]/,/## \[/p" CHANGELOG.md | sed '$d')

# Stage all changes
git add .

# Commit changes with the changelog entry
git commit -m "Version $VERSION

$CHANGELOG_ENTRY"

# Create a new tag for the version
git tag -a "v$VERSION" -m "Version $VERSION"

# Push changes and tags to remote repository
git push origin main
git push origin "v$VERSION"

echo "Changes for version $VERSION have been committed and pushed."
