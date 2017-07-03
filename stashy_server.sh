#!/bin/sh
source .env; gunicorn -w $(( 2 * `cat /proc/cpuinfo | grep 'core id' | wc -l` + 1 )) app:api
