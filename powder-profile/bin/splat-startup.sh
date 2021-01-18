#!/bin/bash

EMUBOOT=/var/emulab/boot
REPODIR=/local/repository

cd $REPODIR
git submodule update --init --remote -- splat || \
    { echo "Failed to update git submodules!" && exit 1; }

sudo rm -r /local/repository/shout
sudo apt-get update -y
sudo apt-get install -y splat

exit 0
