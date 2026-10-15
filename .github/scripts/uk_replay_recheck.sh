#!/usr/bin/env bash
# The record job's second guard, where no candidate code has run: a refused
# output is dropped, so the recorder writes a failed receipt and nothing of
# it reaches the public replay-state branch.
set -euo pipefail
if ! python3 -I .github/scripts/uk_replay_output_guard.py output; then
  echo "::error::the run's output was refused; recording a failed receipt"
  rm -rf output
fi
