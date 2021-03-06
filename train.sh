#!/usr/bin/env bash
nvidia-docker build -t mas_image$2 .
for (( ; ; ))
do
    nvidia-docker stop mas_image$2
    nvidia-docker system prune
    nvidia-docker run --memory="4g" --cpus="8" -e DEVICE=$1 -it mas_image$2
done
