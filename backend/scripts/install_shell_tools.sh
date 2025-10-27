#!/usr/bin/sh

apt update
apt install -y vim procps
rm -rf /var/lib/apt/lists/*
