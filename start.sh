#!/usr/bin/env bash
tmux new-session -d -s "server" "source ~/.bashrc0 && cd ~/MasBot && java -jar target/drl-1.0-SNAPSHOT-bin.jar 10000 32 hyperparams"
tmux new-session -d -s "client1" "bash ~/Runners/train.sh 1 1"
tmux new-session -d -s "client2" "bash ~/Runners/train.sh 2 2"
tmux new-session -d -s "client3" "bash ~/Runners/train.sh 3 3"