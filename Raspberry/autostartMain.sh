#!/bin/bash
sleep 5 
nmcli con up Sara
sleep 5
cd /home/luca/git/SARA/Raspberry/
source bin/activate
python main.py

