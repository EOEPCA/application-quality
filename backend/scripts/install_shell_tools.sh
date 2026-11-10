#!/usr/bin/sh

apt update
apt install -y vim procps htop
rm -rf /var/lib/apt/lists/*
