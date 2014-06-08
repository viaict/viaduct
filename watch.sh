#!/bin/bash
# source: http://stackoverflow.com/questions/9023164/in-bash-how-can-i-run-multiple-infinitely-running-commands-and-cancel-them-all

grunt dev
compass watch . &
PIDS[0]=$!

grunt watch &
PIDS[1]=$!

python run.py
PIDS[2]=$!


trap "kill ${PIDS[*]}" SIGINT

wait
