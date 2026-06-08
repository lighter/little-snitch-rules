#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$script_dir"

shopt -s nullglob

current_time=$(date +'%Y-%m-%d %H:%M:%S')
existing_rules=( ./*.lsrules )
if ((${#existing_rules[@]})); then
  rm -f -- "${existing_rules[@]}"
fi

python3 getRules.py

generated_rules=( ./*.lsrules )
if ((${#generated_rules[@]})); then
  git add -- index.html "${generated_rules[@]}"
else
  git add -- index.html
fi

git commit -m "update rule - $current_time"
git push origin main
