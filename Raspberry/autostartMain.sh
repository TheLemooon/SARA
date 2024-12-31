#!/bin/bash
sleep 5 
sudo nmcli con up Sara
sleep 5
cd /home/luca/git/SARA/Raspberry/
source bin/activate
python3 main.py

