#!/usr/bin/env bash
docker build -t mas_image$1 .
for (( ; ; ))
do
    docker run -it -p $1:$1 -e PROB=$2 -e PORT=$1 mas_image$1
done
