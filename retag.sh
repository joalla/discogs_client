#!/bin/bash
# 1) Deletes the git tag passed in $1:
#    - locally
#    - on the remote passed in $2
# 2) Tags HEAD again with the given version number,
# 3) and pushes commits and tags again to remote
# Additional push options can be passed in $3.

if [[ -z $1 ]] || [[ -z $2 ]]; then
    echo "usage: ./retag.sh <version> <remote> [additional push options]"
    exit 1
fi

set -x
VERS=$1
REMOTE=$2
PUSH_OPTS="$3"

git tag -d $VERS
git push $REMOTE --delete $VERS
git tag $VERS
git push
git push $REMOTE --tags --follow-tags $PUSH_OPTS
