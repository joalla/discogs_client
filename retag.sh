#!/bin/bash

if [[ -z $1 ]]; then
    echo "usage: ./retag.sh <version>  # omit v prefix"
    exit 1
fi
PUSH_OPTS="$2"

set -x
VERS=$1

git tag -d v$VERS; git push origin --delete v$VERS; git tag v$VERS; git push $PUSH_OPTS; git push --tags
