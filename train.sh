#!/usr/bin/env bash
for (( ; ; ))
do
    docker run -it -p 1612:1612 -p 1613:1613 -p 1614:1614 -p 1615:1615 -p 1616:1616 -e PROB=$1 mas_image
done
