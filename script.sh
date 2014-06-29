#!/bin/bash

#=====================================================================================
#
# Filename: script.sh
#
# Description: Cloud Orchestration
#
# Author: Ramakrishna Kota (201250929)
#
#=====================================================================================
#

echo installing software
apt-get install flask
apt-get install python-bottle
echo Run cloud app
python src/sample.py $1 $2 $3
echo server running port 50000
echo Opening browser to manage cloud service
echo gnome-open http://localhost:50000
