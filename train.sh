#!/usr/bin/env bash
docker build -t mas_image$2 .
for (( ; ; ))
do
    docker stop $(docker ps -aq)
    docker run -e $1 -it mas_image$2
done
