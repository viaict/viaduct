#!/bin/sh

# Exit on any error
set -e


# Default git params
if [ $# -eq 0 ]; then
    gitparams='diff HEAD'
else
    gitparams=$1
fi

# Default Flake8 path
if [ $# -le 1 ]; then
    flake8path=venv/bin/flake8
else
    flake8path=$2
fi


# Check python file changes for flake8 errors and ignore migrations since they
# are auto generated
git $gitparams --name-only | grep .py\$ | grep --invert-match '^migrations/versions/' | xargs --no-run-if-empty $flake8path

# Check for JSHint errors in changed files except for minified files since
# these are not created by us
git $gitparams --name-only | grep .js\$ | grep --invert-match '\.min\.' | xargs --no-run-if-empty jshint
