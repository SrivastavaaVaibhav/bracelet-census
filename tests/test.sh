#!/bin/bash
# Runs the verifier and writes a 0/1 reward.
mkdir -p /logs/verifier
pip install --quiet pytest==8.3.3 >/dev/null 2>&1 || true
if python3 -m pytest -q "$(dirname "$0")/test_outputs.py"; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi
