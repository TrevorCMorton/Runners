#!/usr/bin/env bash
nvidia-docker build -t mas_image$2 .
for (( ; ; ))
do
    nvidia-docker stop $(docker ps -aq)
    nvidia-docker run --memory="4g" --cpus="8" -e DEVICE=$1 -it mas_image$2
done
