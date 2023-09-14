#!/bin/bash
current_time=$(date +'%Y-%m-%d %H:%M:%S')
python getRules.py
git add .
git commit -m "update rule - $current_time"
# git push origin main
