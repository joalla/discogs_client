#!/bin/bash
# Wrapper script for bumpversion/bump2version python package.
# Requires: pip install bump2version
#
# Increments major, minor or patch part of version in configured files
# (.bumpversion.cfg). Can be savely executed to see what would be bumped. To
# really change and commit, a second cli arg "doit" has to be passed.

#set -x
PART=$1

if [ -z $1 ]; then
    echo "Bumps version, commits and tags."
    echo "Usage: ./bump.s <major|minor|patch> [doit]"
    exit 0
fi

if [[ "$2" == "doit" ]]; then
    bumpversion $PART --verbose
    echo ""
    echo "All good? Then push commits and tags:"
    echo "git push && git push --tags"
else
    echo -e "\nTHIS IS A DRY-RUN\n"
    bumpversion $PART --verbose --dry-run
fi
