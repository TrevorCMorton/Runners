#!/usr/bin/env bash
docker build -t mas_image$1 .
for (( ; ; ))
do
    docker stop $(docker ps -aq)
    docker run --device=/dev/dri/card0 -it mas_image$1
done
