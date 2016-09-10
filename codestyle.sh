#!/bin/bash

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
# are auto generated, ignore deleted files.
py_files=$(git $gitparams --name-status | grep ^[^D].*.py\$ | cut -d'	' -f2- | grep --invert-match '^migrations/versions/')
if [[ $? -eq 0 ]]; then
  echo $py_files | xargs $flake8path
fi

# Check for JSHint errors in changed files except for minified files since
# these are not created by us, ignore deleted files.
js_files=$(git $gitparams --name-status | grep ^[^D].*.js\$ | cut -d'	' -f2- | grep --invert-match '\.min\.')
if [[ $? -eq 0 ]]; then
  echo $js_files | xargs jshint
fi

# Exit on any error
set -e

# Fuzzy means translations are changed and probably incorrect
! grep fuzzy app/translations/nl/LC_MESSAGES/messages.po > /dev/null || \
    ! echo "The dutch translations file contained fuzzy translations"
