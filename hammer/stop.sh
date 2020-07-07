#!/bin/bash
pkill chrome
echo 3 > /proc/sys/vm/drop_caches
rm -rf /tmp/.org.chromium*