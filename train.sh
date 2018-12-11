#!/usr/bin/env bash
docker build -t mas_image$1 .
for (( ; ; ))
do
    docker stop $(docker ps -aq)
    docker run -it mas_image$1
done
