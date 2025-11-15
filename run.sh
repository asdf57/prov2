#!/bin/bash

docker build -t rtest:latest .

if [ -z "$(docker ps -q -f name=rtest)" ]; then
    echo "Container rtest is not running. Starting it now..."
else
    echo "Container rtest is already running. Stopping it first..."
    docker stop rtest
    docker rm rtest
fi

docker run \
    -e SSH_KEY="$(cat ~/.ssh/git_provisioning_key)" \
    -e CONCOURSE_URL="${CONCOURSE_URL}" \
    -e CONCOURSE_USERNAME="${CONCOURSE_USERNAME}" \
    -e CONCOURSE_PASSWORD="${CONCOURSE_PASSWORD}" \
    -e CONCOURSE_TEAM="${CONCOURSE_TEAM}" \
    -e CONCOURSE_COMMANDS_PIPELINE="${CONCOURSE_COMMANDS_PIPELINE}" \
    -e CONCOURSE_COMMANDS_RESOURCE="${CONCOURSE_COMMANDS_RESOURCE}" \
    -e CONCOURSE_OAUTH_CLIENT_ID="${CONCOURSE_OAUTH_CLIENT_ID}" \
    -e CONCOURSE_OAUTH_CLIENT_SECRET="${CONCOURSE_OAUTH_CLIENT_SECRET}" \
    --name rtest \
    --rm \
    -it \
    -p 3000:3000 \
    rtest:latest
