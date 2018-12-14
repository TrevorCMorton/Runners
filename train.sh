#!/usr/bin/env bash
docker build -t mas_image$2 .
for (( ; ; ))
do
    docker stop $(docker ps -aq)
    docker run --memory="4g" --cpus="8" -e DEVICE=$1 -it mas_image$2
done
