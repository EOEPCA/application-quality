#!/usr/bin/sh

curl -fSLo /tmp/k9s.deb https://github.com/derailed/k9s/releases/download/v0.50.16/k9s_linux_amd64.deb
apt install /tmp/k9s.deb
rm /tmp/k9s.deb