#!/usr/bin/env bash
tmux kill-server
docker stop $(docker ps -aq)