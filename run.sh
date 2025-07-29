#!/bin/bash

docker build -t rtest:latest .

if [ -z "$(docker ps -q -f name=rtest)" ]; then
    echo "Container rtest is not running. Starting it now..."
else
    echo "Container rtest is already running. Stopping it first..."
    docker stop rtest
    docker rm rtest
fi

docker run -e SSH_KEY="$(cat ~/.ssh/git_provisioning_key)" --name rtest --rm -it -p 3000:3000 rtest:latest
