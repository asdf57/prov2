#!/bin/bash

eval "$(ssh-agent -s)" >/dev/null 2>&1

mkdir -p /root/.ssh

if [[ -f /run/secrets/git_provisioning_key ]]; then
    echo "Detected that we are running in docker-compose!"
    SSH_KEY=$(cat /run/secrets/git_provisioning_key)
fi

echo "$SSH_KEY" > /root/.ssh/git_provisioning_key
chmod 600 /root/.ssh/git_provisioning_key
ssh-add /root/.ssh/git_provisioning_key
ssh-keyscan -t rsa github.com >> /root/.ssh/known_hosts

uvicorn app.main:app --host 0.0.0.0 --port 3000
