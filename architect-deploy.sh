#!/usr/bin/env bash

# while true; do architect deploy architect.yml -a blinkdeploys -e blinkdeploys-env -y; sleep 72000; done
architect deploy architect.yml -a blinkdeploys -e blinkdeploys-env
