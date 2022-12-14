#!/bin/bash
sudo apt update && sudo apt upgrade -y
sudo apt-get install ca-certificates curl gnupg lsb-release software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" -y
sudo apt-get update
sudo apt-get install docker-ce -y
sudo usermod -aG docker $USER
