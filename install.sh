#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 22

cd /home/carsten/DEVPROJECTS/ks-polonia/website
rm -rf node_modules package-lock.json

echo "Starting npm install at $(date)" > /tmp/npm-install-log.txt
npm install --legacy-peer-deps >> /tmp/npm-install-log.txt 2>&1
echo "npm install exited with code $? at $(date)" >> /tmp/npm-install-log.txt
ls -la node_modules/.bin/astro >> /tmp/npm-install-log.txt 2>&1
echo "DONE" >> /tmp/npm-install-log.txt
