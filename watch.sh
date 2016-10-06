#!/bin/bash
# source: http://stackoverflow.com/questions/9023164/in-bash-how-can-i-run-multiple-infinitely-running-commands-and-cancel-them-all

grunt dev
compass watch . &
PIDS[0]=$!

grunt watch &
PIDS[1]=$!

python manage.py jade &
PIDS[2]=$!

python manage.py runserver &
PIDS[3]=$!


trap "kill ${PIDS[*]}" SIGINT

wait
